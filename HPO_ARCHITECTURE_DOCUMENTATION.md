# HPO Tree Visualizer - Complete Architecture Documentation

## Overview

The HPO Tree Visualizer is a high-performance web application for exploring the Human Phenotype Ontology (HPO) with interactive tree visualization, real-time search, and on-demand data loading. The system consists of a FastAPI backend and a modern React-like frontend that efficiently handles 19,778+ HPO terms without performance issues.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│   Frontend      │◄──────────────────►│   Backend       │
│   (HTML/JS)     │                    │   (FastAPI)     │
└─────────────────┘                    └─────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│   vis.js        │                    │   HPO Data      │
│   Visualization │                    │   (JSON)        │
└─────────────────┘                    └─────────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python 3.9+** - Runtime

**Frontend:**
- **Vanilla JavaScript** - No framework dependencies
- **vis.js** - Network visualization library
- **HTML5/CSS3** - Modern web standards
- **Fetch API** - HTTP client

**Data:**
- **HPO JSON** - Human Phenotype Ontology data
- **19,778 nodes** - HPO terms
- **23,584 relationships** - is_a relationships

## Backend Architecture

### Core Components

#### 1. FastAPI Application (`backend.py`)

```python
# Main application structure
app = FastAPI(title="HPO API", version="1.0.0")

# Global data storage
hpo_data = None
nodes = {}
edges = []
parent_children = defaultdict(list)
child_parents = defaultdict(list)
```

#### 2. Data Models (Pydantic)

```python
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
```

#### 3. Data Processing Pipeline

**Startup Process:**
1. Load HPO JSON data from file
2. Process nodes into structured format
3. Build parent-child relationships
4. Create lookup dictionaries for fast access

**Data Structure:**
```python
nodes = {
    "http://purl.obolibrary.org/obo/HP_0000001": {
        "id": "http://purl.obolibrary.org/obo/HP_0000001",
        "label": "All",
        "full_id": "HP_0000001",
        "definition": "",
        "synonyms": [],
        "parents": [],
        "children": ["HP_0000005", "HP_0000118", ...]
    }
}
```

### API Endpoints

#### 1. Statistics Endpoint
```http
GET /api/stats
```
**Response:**
```json
{
    "total_nodes": 19778,
    "total_edges": 23584,
    "root_node": "http://purl.obolibrary.org/obo/HP_0000001"
}
```

#### 2. Search Endpoint
```http
GET /api/search?q=kidney&page=1&page_size=20
```
**Parameters:**
- `q` (required): Search query (min 2 characters)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Results per page (default: 20, max: 100)

**Response:**
```json
{
    "nodes": [
        {
            "id": "http://purl.obolibrary.org/obo/HP_0000119",
            "label": "Abnormality of the genitourinary system",
            "full_id": "HP_0000119",
            "definition": "The presence of any abnormality...",
            "synonyms": ["Abnormality of the GU system"],
            "parents": ["http://purl.obolibrary.org/obo/HP_0000118"],
            "children": ["http://purl.obolibrary.org/obo/HP_0000078"]
        }
    ],
    "total": 45,
    "page": 1,
    "page_size": 20
}
```

#### 3. Node Details Endpoint
```http
GET /api/node/{node_id:path}
```
**URL Encoding:** Node IDs are URL-encoded (e.g., `http%3A//purl.obolibrary.org/obo/HP_0000001`)

**Response:**
```json
{
    "id": "http://purl.obolibrary.org/obo/HP_0000001",
    "label": "All",
    "full_id": "HP_0000001",
    "definition": "",
    "synonyms": [],
    "parents": [],
    "children": ["http://purl.obolibrary.org/obo/HP_0000005", ...]
}
```

#### 4. Subgraph Endpoint
```http
GET /api/subgraph/{node_id:path}?depth=2
```
**Parameters:**
- `node_id`: Center node for subgraph
- `depth` (optional): Depth of subgraph (1-5, default: 2)

**Response:**
```json
{
    "nodes": [
        {
            "id": "http://purl.obolibrary.org/obo/HP_0000001",
            "label": "All",
            "full_id": "HP_0000001",
            "definition": "",
            "synonyms": [],
            "parents": [],
            "children": ["http://purl.obolibrary.org/obo/HP_0000005"]
        }
    ],
    "edges": [
        {
            "from": "http://purl.obolibrary.org/obo/HP_0000005",
            "to": "http://purl.obolibrary.org/obo/HP_0000001"
        }
    ]
}
```

#### 5. Parent/Children Endpoints
```http
GET /api/node/{node_id:path}/parents
GET /api/node/{node_id:path}/children
```

### Backend Features

#### 1. URL Encoding Handling
```python
@app.get("/api/node/{node_id:path}")
async def get_node(node_id: str):
    decoded_node_id = urllib.parse.unquote(node_id)
    # Process with decoded ID
```

#### 2. Search Algorithm
- **Multi-field search**: Label, full_id, synonyms
- **Relevance scoring**: Exact matches first, then by label length
- **Pagination**: Efficient large result handling
- **Case-insensitive**: User-friendly search

#### 3. Subgraph Generation
- **Breadth-first traversal**: Efficient graph exploration
- **Depth limiting**: Prevents excessive data loading
- **Relationship tracking**: Identifies parent/child relationships
- **Edge generation**: Creates visualization edges

## Frontend Architecture

### Core Components

#### 1. Main Application Class
```javascript
class HPOExplorer {
    constructor() {
        this.network = null;
        this.selectedNodeId = null;
        this.currentDepth = 2;
        this.apiBaseUrl = 'http://localhost:8000/api';
    }
}
```

#### 2. Visualization Engine (vis.js)
```javascript
const options = {
    nodes: {
        shape: 'box',
        margin: 10,
        widthConstraint: { maximum: 200 },
        font: { size: 14, face: 'Arial' },
        borderWidth: 2,
        shadow: true
    },
    edges: {
        arrows: { to: { enabled: true, scaleFactor: 0.5 } },
        smooth: { type: 'cubicBezier', roundness: 0.4 },
        width: 2
    },
    layout: {
        hierarchical: {
            direction: 'DU',  // Down-Up (general to specific)
            sortMethod: 'directed',
            shakeTowards: 'roots',
            levelSeparation: 100,
            nodeSpacing: 50
        }
    },
    physics: {
        enabled: true,
        hierarchicalRepulsion: {
            centralGravity: 0.0,
            springLength: 100,
            springConstant: 0.01,
            nodeDistance: 150,
            damping: 0.09
        }
    }
};
```

#### 3. Color Coding System
```javascript
// Node color scheme
const colors = {
    selected: { background: '#6c5ce7', border: '#5f3dc4' },
    parent: { background: '#00b894', border: '#00896e' },
    child: { background: '#4a90e2', border: '#3a7bc8' },
    default: { background: '#4a90e2', border: '#3a7bc8' }
};
```

### Frontend Features

#### 1. Real-time Search
```javascript
async function handleSearchInput(e) {
    const query = e.target.value.trim();
    
    // Debounce search
    if (searchTimeout) clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(() => {
        performSearch(query, true);
    }, 300);
}
```

#### 2. On-demand Data Loading
```javascript
async function selectNode(nodeId) {
    // Load node details
    const nodeResponse = await fetch(`${apiBaseUrl}/node/${encodeURIComponent(nodeId)}`);
    const node = await nodeResponse.json();
    
    // Load subgraph for visualization
    const subgraphResponse = await fetch(`${apiBaseUrl}/subgraph/${encodeURIComponent(nodeId)}?depth=${currentDepth}`);
    const subgraph = await subgraphResponse.json();
    
    // Update visualization
    updateVisualization(subgraph);
}
```

#### 3. Interactive Navigation
- **Click to select**: Click any node to center the view
- **Parent/child navigation**: Click items in info panel
- **Depth control**: Slider to adjust visualization depth
- **Search autocomplete**: Dropdown with search suggestions

#### 4. Responsive Design
```css
.main-content {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 20px;
}

@media (max-width: 992px) {
    .main-content {
        grid-template-columns: 1fr;
    }
}
```

## Data Flow

### 1. Application Initialization
```
1. Page loads → Check vis.js availability
2. Connect to API → Load statistics
3. Initialize network → Create empty visualization
4. Load root node → Display initial tree
```

### 2. Search Flow
```
1. User types → Debounced input handler
2. API call → /api/search?q=query
3. Display results → Dropdown with suggestions
4. User selects → Load node and subgraph
5. Update visualization → Show selected node
```

### 3. Node Selection Flow
```
1. User clicks node → selectNode(nodeId)
2. Load node details → /api/node/{nodeId}
3. Load subgraph → /api/subgraph/{nodeId}?depth=N
4. Update visualization → Render new tree
5. Update info panel → Show node details
6. Load relationships → Show parents/children
```

## Performance Optimizations

### Backend Optimizations
1. **In-memory data structures**: Fast lookups with dictionaries
2. **Relationship pre-computation**: Parent/child maps built at startup
3. **Pagination**: Limit search results to prevent large responses
4. **URL encoding handling**: Efficient node ID processing
5. **CORS configuration**: Proper cross-origin support

### Frontend Optimizations
1. **On-demand loading**: Only load data when needed
2. **Debounced search**: Prevent excessive API calls
3. **Efficient rendering**: vis.js optimized for large graphs
4. **Lazy relationship loading**: Load parent/child details asynchronously
5. **Responsive design**: Works on all device sizes

## File Structure

```
HPO/
├── backend.py              # FastAPI backend server
├── frontend-api.html       # Main frontend application
├── hp.json                 # HPO data (536,907 lines)
├── vis-network.min.js      # Visualization library
├── requirements.txt        # Python dependencies
├── package.json           # Node.js metadata
└── README.md              # Documentation
```

## Dependencies

### Backend Dependencies
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
```

### Frontend Dependencies
- **vis.js**: Network visualization (CDN or local)
- **Modern browser**: ES6+ support required
- **No build process**: Pure HTML/CSS/JS

## Integration Guide

### 1. Backend Integration
```python
# Add to existing FastAPI app
from fastapi import FastAPI
from hpo_backend import hpo_router

app = FastAPI()
app.include_router(hpo_router, prefix="/api/hpo")
```

### 2. Frontend Integration
```javascript
// Add to existing React/Vue/Angular app
import HPOVisualizer from './components/HPOVisualizer';

// Or use as standalone component
const hpoContainer = document.getElementById('hpo-visualizer');
const hpoApp = new HPOVisualizer(hpoContainer, {
    apiBaseUrl: '/api/hpo',
    initialNode: 'HP_0000001'
});
```

### 3. Data Integration
```python
# Custom data source
class CustomHPOBackend:
    def __init__(self, data_source):
        self.data_source = data_source
    
    async def get_node(self, node_id):
        # Custom implementation
        pass
```

## Configuration Options

### Backend Configuration
```python
# Environment variables
HPO_DATA_PATH = "path/to/hp.json"
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:3000"]
```

### Frontend Configuration
```javascript
const config = {
    apiBaseUrl: 'http://localhost:8000/api',
    maxSearchResults: 20,
    defaultDepth: 2,
    maxDepth: 5,
    searchDebounceMs: 300,
    nodeColors: {
        selected: '#6c5ce7',
        parent: '#00b894',
        child: '#4a90e2',
        default: '#4a90e2'
    }
};
```

## Error Handling

### Backend Error Handling
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### Frontend Error Handling
```javascript
try {
    const response = await fetch(`${apiBaseUrl}/node/${nodeId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
} catch (error) {
    console.error('Error loading node:', error);
    showStatus('Error: ' + error.message, 'error');
}
```

## Security Considerations

1. **CORS Configuration**: Properly configured for production
2. **Input Validation**: Pydantic models validate all inputs
3. **Rate Limiting**: Consider implementing for production
4. **Authentication**: Add if needed for protected access
5. **Data Sanitization**: All user inputs are sanitized

## Scalability Considerations

1. **Database Integration**: Replace in-memory storage with database
2. **Caching**: Add Redis for frequently accessed data
3. **Load Balancing**: Multiple backend instances
4. **CDN**: Serve static assets from CDN
5. **Monitoring**: Add logging and metrics

## Testing Strategy

### Backend Testing
```python
import pytest
from fastapi.testclient import TestClient

def test_search_endpoint():
    response = client.get("/api/search?q=kidney")
    assert response.status_code == 200
    assert "nodes" in response.json()
```

### Frontend Testing
```javascript
// Unit tests for core functions
describe('HPOExplorer', () => {
    test('should initialize with root node', () => {
        const explorer = new HPOExplorer();
        expect(explorer.selectedNodeId).toBe('HP_0000001');
    });
});
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
1. **Environment Variables**: Use for configuration
2. **Logging**: Structured logging with appropriate levels
3. **Health Checks**: Add `/health` endpoint
4. **Metrics**: Add Prometheus metrics
5. **SSL/TLS**: Use HTTPS in production

This architecture provides a robust, scalable foundation for HPO visualization that can be easily integrated into existing applications while maintaining high performance and user experience.
