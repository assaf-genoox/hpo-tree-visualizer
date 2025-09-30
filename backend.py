from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import re
from collections import defaultdict
import uvicorn

app = FastAPI(title="HPO API", description="Human Phenotype Ontology API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded data
hpo_data = None
nodes = {}
edges = []
parent_children = defaultdict(list)
child_parents = defaultdict(list)

class NodeInfo(BaseModel):
    id: str
    label: str
    full_id: str
    definition: Optional[str] = None
    synonyms: List[str] = []
    parents: List[str] = []
    children: List[str] = []

class SearchResult(BaseModel):
    nodes: List[NodeInfo]
    total: int
    page: int
    page_size: int

class SubgraphResponse(BaseModel):
    nodes: List[NodeInfo]
    edges: List[Dict[str, str]]

@app.on_event("startup")
async def load_hpo_data():
    """Load HPO data on startup"""
    global hpo_data, nodes, edges, parent_children, child_parents
    
    print("Loading HPO data...")
    try:
        with open('hp.json', 'r') as f:
            hpo_data = json.load(f)
        
        # Process nodes
        for node in hpo_data['graphs'][0]['nodes']:
            node_id = node['id']
            nodes[node_id] = {
                'id': node_id,
                'label': node.get('lbl') or 'Unknown',
                'full_id': node_id.replace('http://purl.obolibrary.org/obo/', ''),
                'definition': node.get('meta', {}).get('definition', {}).get('val', ''),
                'synonyms': [s['val'] for s in node.get('meta', {}).get('synonyms', [])],
                'parents': [],
                'children': []
            }
        
        # Process edges and build relationships
        for edge in hpo_data['graphs'][0]['edges']:
            if edge['pred'] == 'is_a':
                child_id = edge['sub']
                parent_id = edge['obj']
                
                if child_id in nodes and parent_id in nodes:
                    parent_children[parent_id].append(child_id)
                    child_parents[child_id].append(parent_id)
                    
                    nodes[child_id]['parents'].append(parent_id)
                    nodes[parent_id]['children'].append(child_id)
        
        edges = hpo_data['graphs'][0]['edges']
        print(f"Loaded {len(nodes)} nodes and {len(edges)} edges")
        
    except Exception as e:
        print(f"Error loading HPO data: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "HPO API is running", "total_nodes": len(nodes)}

@app.get("/api/stats")
async def get_stats():
    """Get basic statistics about the HPO data"""
    return {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "root_node": "http://purl.obolibrary.org/obo/HP_0000001"
    }

@app.get("/api/search", response_model=SearchResult)
async def search_nodes(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page")
):
    """Search for HPO nodes by label, ID, or synonyms"""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    query_lower = q.lower()
    results = []
    
    # Search through nodes
    for node_id, node in nodes.items():
        # Check label, full_id, and synonyms
        if (query_lower in node['label'].lower() or 
            query_lower in node['full_id'].lower() or
            any(query_lower in syn.lower() for syn in node['synonyms'])):
            
            # Create NodeInfo with relationships
            node_info = NodeInfo(
                id=node_id,
                label=node['label'],
                full_id=node['full_id'],
                definition=node['definition'],
                synonyms=node['synonyms'],
                parents=node['parents'],
                children=node['children']
            )
            results.append(node_info)
    
    # Sort by relevance (exact matches first, then by label length)
    results.sort(key=lambda x: (
        0 if query_lower in x.label.lower() or query_lower in x.full_id.lower() else 1,
        len(x.label)
    ))
    
    # Pagination
    total = len(results)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = results[start:end]
    
    return SearchResult(
        nodes=paginated_results,
        total=total,
        page=page,
        page_size=page_size
    )

@app.get("/api/node/{node_id:path}", response_model=NodeInfo)
async def get_node(node_id: str):
    """Get detailed information about a specific node"""
    # Decode URL encoding
    import urllib.parse
    decoded_node_id = urllib.parse.unquote(node_id)
    
    if decoded_node_id not in nodes:
        raise HTTPException(status_code=404, detail=f"Node not found: {decoded_node_id}")
    
    node = nodes[decoded_node_id]
    return NodeInfo(
        id=decoded_node_id,
        label=node['label'],
        full_id=node['full_id'],
        definition=node['definition'],
        synonyms=node['synonyms'],
        parents=node['parents'],
        children=node['children']
    )

@app.get("/api/node/{node_id:path}/parents")
async def get_parents(node_id: str):
    """Get parent nodes of a specific node"""
    import urllib.parse
    decoded_node_id = urllib.parse.unquote(node_id)
    
    if decoded_node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    
    parent_ids = nodes[decoded_node_id]['parents']
    parent_nodes = []
    
    for parent_id in parent_ids:
        if parent_id in nodes:
            parent = nodes[parent_id]
            parent_nodes.append(NodeInfo(
                id=parent_id,
                label=parent['label'],
                full_id=parent['full_id'],
                definition=parent['definition'],
                synonyms=parent['synonyms'],
                parents=parent['parents'],
                children=parent['children']
            ))
    
    return {"parents": parent_nodes}

@app.get("/api/node/{node_id:path}/children")
async def get_children(node_id: str):
    """Get child nodes of a specific node"""
    import urllib.parse
    decoded_node_id = urllib.parse.unquote(node_id)
    
    if decoded_node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    
    child_ids = nodes[decoded_node_id]['children']
    child_nodes = []
    
    for child_id in child_ids:
        if child_id in nodes:
            child = nodes[child_id]
            child_nodes.append(NodeInfo(
                id=child_id,
                label=child['label'],
                full_id=child['full_id'],
                definition=child['definition'],
                synonyms=child['synonyms'],
                parents=child['parents'],
                children=child['children']
            ))
    
    return {"children": child_nodes}

@app.get("/api/subgraph/{node_id:path}", response_model=SubgraphResponse)
async def get_subgraph(
    node_id: str,
    depth: int = Query(2, ge=1, le=5, description="Depth of subgraph")
):
    """Get a subgraph around a specific node for visualization"""
    import urllib.parse
    decoded_node_id = urllib.parse.unquote(node_id)
    
    if decoded_node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    
    visited = set()
    result_nodes = []
    result_edges = []
    queue = [(decoded_node_id, 0, False, False)]  # (node_id, level, is_parent, is_child)
    visited.add(decoded_node_id)
    
    while queue:
        current_id, level, is_parent, is_child = queue.pop(0)
        current_node = nodes[current_id]
        
        # Add node to results
        result_nodes.append(NodeInfo(
            id=current_id,
            label=current_node['label'],
            full_id=current_node['full_id'],
            definition=current_node['definition'],
            synonyms=current_node['synonyms'],
            parents=current_node['parents'],
            children=current_node['children']
        ))
        
        # Add edges
        for parent_id in current_node['parents']:
            result_edges.append({"from": current_id, "to": parent_id})
        
        # Continue expanding if within depth limit
        if level < depth:
            # Add parents
            for parent_id in current_node['parents']:
                if parent_id not in visited and parent_id in nodes:
                    visited.add(parent_id)
                    queue.append((parent_id, level + 1, current_id == node_id, False))
            
            # Add children
            for child_id in current_node['children']:
                if child_id not in visited and child_id in nodes:
                    visited.add(child_id)
                    queue.append((child_id, level + 1, False, current_id == node_id))
    
    return SubgraphResponse(nodes=result_nodes, edges=result_edges)

# Serve static files (frontend)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
