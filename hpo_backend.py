from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import urllib.parse
from collections import defaultdict, deque
from typing import List, Dict, Optional

app = FastAPI(title="HPO API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Global data storage
hpo_data = None
nodes = {}
edges = []
parent_children = defaultdict(list)
child_parents = defaultdict(list)
hpo_stats = {}

# Pydantic models
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
    """Load and process HPO data on startup"""
    global hpo_data, nodes, edges, parent_children, child_parents, hpo_stats
    
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
                    nodes[child_id]['parents'].append(parent_id)
                    nodes[parent_id]['children'].append(child_id)
                    parent_children[parent_id].append(child_id)
                    child_parents[child_id].append(parent_id)
                    edges.append({'from': child_id, 'to': parent_id})

        # Calculate statistics
        hpo_stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'root_node': "http://purl.obolibrary.org/obo/HP_0000001"
        }
        
        print(f"Loaded {len(nodes)} nodes and {len(edges)} edges")
        
    except Exception as e:
        print(f"Error loading HPO data: {e}")
        raise

@app.get("/api/stats")
async def get_stats():
    """Get HPO statistics"""
    return hpo_stats

@app.get("/api/search", response_model=SearchResult)
async def search_hpo_terms(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page")
):
    """Search HPO terms with pagination"""
    query = q.lower()
    matching_nodes = []
    
    for node_id, node_data in nodes.items():
        # Search in label, full_id, and synonyms
        if (query in node_data['label'].lower() or 
            query in node_data['full_id'].lower() or 
            any(query in s.lower() for s in node_data['synonyms'])):
            
            matching_nodes.append(NodeInfo(
                id=node_id,
                label=node_data['label'],
                full_id=node_data['full_id'],
                definition=node_data['definition'],
                synonyms=node_data['synonyms'],
                parents=node_data['parents'],
                children=node_data['children']
            ))
    
    # Sort by relevance (exact matches first, then by label length)
    matching_nodes.sort(key=lambda x: (
        0 if query in x.label.lower() else 1,
        len(x.label)
    ))
    
    # Pagination
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_nodes = matching_nodes[start_index:end_index]
    
    return SearchResult(
        nodes=paginated_nodes,
        total=len(matching_nodes),
        page=page,
        page_size=page_size
    )

@app.get("/api/node/{node_id:path}", response_model=NodeInfo)
async def get_node(node_id: str):
    """Get detailed information about a specific node"""
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
    decoded_node_id = urllib.parse.unquote(node_id)
    
    if decoded_node_id not in nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    
    visited = set()
    result_nodes = []
    result_edges = []
    queue = deque([(decoded_node_id, 0)])
    visited.add(decoded_node_id)
    
    # Add the central node first
    central_node_data = nodes[decoded_node_id]
    result_nodes.append(NodeInfo(
        id=central_node_data['id'],
        label=central_node_data['label'],
        full_id=central_node_data['full_id'],
        definition=central_node_data['definition'],
        synonyms=central_node_data['synonyms'],
        parents=central_node_data['parents'],
        children=central_node_data['children']
    ))
    
    while queue:
        current_id, level = queue.popleft()
        current_node = nodes[current_id]
        
        if level < depth:
            # Add parents
            for parent_id in current_node['parents']:
                if parent_id not in visited:
                    visited.add(parent_id)
                    parent_data = nodes[parent_id]
                    result_nodes.append(NodeInfo(
                        id=parent_data['id'],
                        label=parent_data['label'],
                        full_id=parent_data['full_id'],
                        definition=parent_data['definition'],
                        synonyms=parent_data['synonyms'],
                        parents=parent_data['parents'],
                        children=parent_data['children']
                    ))
                    result_edges.append({'from': current_id, 'to': parent_id})
                    queue.append((parent_id, level + 1))
                else:
                    # Ensure edge is added if not already present
                    if not any(e['from'] == current_id and e['to'] == parent_id for e in result_edges):
                        result_edges.append({'from': current_id, 'to': parent_id})
            
            # Add children
            for child_id in current_node['children']:
                if child_id not in visited:
                    visited.add(child_id)
                    child_data = nodes[child_id]
                    result_nodes.append(NodeInfo(
                        id=child_data['id'],
                        label=child_data['label'],
                        full_id=child_data['full_id'],
                        definition=child_data['definition'],
                        synonyms=child_data['synonyms'],
                        parents=child_data['parents'],
                        children=child_data['children']
                    ))
                    result_edges.append({'from': child_id, 'to': current_id})
                    queue.append((child_id, level + 1))
                else:
                    # Ensure edge is added if not already present
                    if not any(e['from'] == child_id and e['to'] == current_id for e in result_edges):
                        result_edges.append({'from': child_id, 'to': current_id})
    
    return SubgraphResponse(nodes=result_nodes, edges=result_edges)

@app.get("/")
async def root():
    """Root endpoint - serve frontend"""
    return FileResponse("hpo_frontend.html")

@app.get("/hpo_frontend.html")
async def frontend():
    """Serve the frontend HTML"""
    return FileResponse("hpo_frontend.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if data is loaded
        if not nodes or len(nodes) == 0:
            return {"status": "loading", "message": "HPO data is still loading"}
        
        return {
            "status": "healthy", 
            "nodes_loaded": len(nodes),
            "edges_loaded": len(edges),
            "message": "HPO Tree Visualizer is ready"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
