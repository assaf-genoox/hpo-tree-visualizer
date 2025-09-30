# HPO Tree Visualizer - Integration Guide

## Quick Start

### 1. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Place your HPO JSON file as 'hp.json' in the same directory
# Download from: https://hpo.jax.org/app/download/ontology

# Run the backend server
python hpo_backend.py
# OR
uvicorn hpo_backend:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup

```bash
# Simply open hpo_frontend.html in a web browser
# Or serve it with any web server:
python -m http.server 8080
# Then visit: http://localhost:8080/hpo_frontend.html
```

## Integration Options

### Option 1: Standalone Application

Use the provided files as-is for a complete standalone HPO visualization tool.

**Files needed:**
- `hpo_backend.py` - Backend API server
- `hpo_frontend.html` - Frontend web interface
- `requirements.txt` - Python dependencies
- `hp.json` - HPO data file

### Option 2: Backend Integration

Integrate the HPO API into your existing FastAPI application.

```python
# In your existing FastAPI app
from fastapi import FastAPI
from hpo_backend import app as hpo_app

app = FastAPI(title="Your App")

# Include HPO routes with prefix
app.mount("/api/hpo", hpo_app)

# Or include specific routes
from hpo_backend import search_hpo_terms, get_node, get_subgraph
app.include_router(hpo_app.router, prefix="/api/hpo")
```

### Option 3: Frontend Component Integration

Integrate the visualization component into your existing web application.

#### React Integration

```jsx
import React, { useEffect, useRef } from 'react';

const HPOVisualizer = ({ apiBaseUrl = 'http://localhost:8000/api' }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    // Load vis.js dynamically
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js';
    script.onload = () => {
      initializeVisualization();
    };
    document.head.appendChild(script);

    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
      }
    };
  }, []);

  const initializeVisualization = () => {
    // Initialize vis.js network
    const nodes = new vis.DataSet([]);
    const edges = new vis.DataSet([]);
    
    const data = { nodes, edges };
    const options = {
      // ... same options as in hpo_frontend.html
    };
    
    networkRef.current = new vis.Network(containerRef.current, data, options);
  };

  return (
    <div className="hpo-visualizer">
      <div ref={containerRef} style={{ width: '100%', height: '600px' }} />
    </div>
  );
};

export default HPOVisualizer;
```

#### Vue.js Integration

```vue
<template>
  <div class="hpo-visualizer">
    <div ref="networkContainer" style="width: 100%; height: 600px;"></div>
  </div>
</template>

<script>
export default {
  name: 'HPOVisualizer',
  props: {
    apiBaseUrl: {
      type: String,
      default: 'http://localhost:8000/api'
    }
  },
  data() {
    return {
      network: null,
      visNodes: null,
      visEdges: null
    };
  },
  mounted() {
    this.loadVisJS().then(() => {
      this.initializeVisualization();
    });
  },
  methods: {
    async loadVisJS() {
      return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js';
        script.onload = resolve;
        document.head.appendChild(script);
      });
    },
    initializeVisualization() {
      // Implementation similar to React version
    }
  }
};
</script>
```

#### Angular Integration

```typescript
// hpo-visualizer.component.ts
import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';

declare const vis: any;

@Component({
  selector: 'app-hpo-visualizer',
  template: '<div #networkContainer style="width: 100%; height: 600px;"></div>'
})
export class HPOVisualizerComponent implements AfterViewInit {
  @ViewChild('networkContainer', { static: true }) networkContainer!: ElementRef;
  
  private network: any;
  private visNodes: any;
  private visEdges: any;

  ngAfterViewInit() {
    this.loadVisJS().then(() => {
      this.initializeVisualization();
    });
  }

  private async loadVisJS(): Promise<void> {
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js';
      script.onload = () => resolve();
      document.head.appendChild(script);
    });
  }

  private initializeVisualization() {
    // Implementation similar to other frameworks
  }
}
```

### Option 4: Custom Data Source Integration

Modify the backend to work with your own data source.

```python
# custom_hpo_backend.py
from hpo_backend import app, NodeInfo, SearchResult, SubgraphResponse
from your_data_source import YourDataProvider

class CustomHPOBackend:
    def __init__(self, data_provider: YourDataProvider):
        self.data_provider = data_provider
    
    async def get_node(self, node_id: str) -> NodeInfo:
        # Custom implementation using your data source
        data = await self.data_provider.get_node(node_id)
        return NodeInfo(
            id=data['id'],
            label=data['label'],
            full_id=data['full_id'],
            definition=data.get('definition'),
            synonyms=data.get('synonyms', []),
            parents=data.get('parents', []),
            children=data.get('children', [])
        )
    
    async def search_nodes(self, query: str, page: int, page_size: int) -> SearchResult:
        # Custom search implementation
        results = await self.data_provider.search(query, page, page_size)
        return SearchResult(
            nodes=[self.convert_to_node_info(r) for r in results['nodes']],
            total=results['total'],
            page=page,
            page_size=page_size
        )

# Replace the original endpoints
@app.get("/api/node/{node_id:path}")
async def get_node(node_id: str):
    custom_backend = CustomHPOBackend(your_data_provider)
    return await custom_backend.get_node(node_id)
```

## Configuration

### Environment Variables

```bash
# Backend configuration
export HPO_DATA_PATH="/path/to/hp.json"
export API_HOST="0.0.0.0"
export API_PORT="8000"
export CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

# Frontend configuration
export VITE_API_BASE_URL="http://localhost:8000/api"
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY hpo_backend.py .
COPY hp.json .

EXPOSE 8000

CMD ["uvicorn", "hpo_backend:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  hpo-backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./hp.json:/app/hp.json
    environment:
      - HPO_DATA_PATH=/app/hp.json
  
  hpo-frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./hpo_frontend.html:/usr/share/nginx/html/index.html
      - ./vis-network.min.js:/usr/share/nginx/html/vis-network.min.js
```

## API Usage Examples

### Search HPO Terms

```javascript
// Search for terms containing "kidney"
const response = await fetch('http://localhost:8000/api/search?q=kidney&page=1&page_size=10');
const data = await response.json();
console.log(data.nodes); // Array of matching HPO terms
```

### Get Node Details

```javascript
// Get details for a specific HPO term
const nodeId = 'http://purl.obolibrary.org/obo/HP_0000119';
const response = await fetch(`http://localhost:8000/api/node/${encodeURIComponent(nodeId)}`);
const node = await response.json();
console.log(node.label); // "Abnormality of the genitourinary system"
```

### Get Subgraph for Visualization

```javascript
// Get subgraph around a node for tree visualization
const nodeId = 'http://purl.obolibrary.org/obo/HP_0000119';
const response = await fetch(`http://localhost:8000/api/subgraph/${encodeURIComponent(nodeId)}?depth=2`);
const subgraph = await response.json();
console.log(subgraph.nodes); // Array of nodes in subgraph
console.log(subgraph.edges); // Array of edges in subgraph
```

### Python API Usage

```python
import requests

# Search HPO terms
response = requests.get('http://localhost:8000/api/search', params={
    'q': 'kidney',
    'page': 1,
    'page_size': 10
})
data = response.json()

# Get node details
node_id = 'http://purl.obolibrary.org/obo/HP_0000119'
response = requests.get(f'http://localhost:8000/api/node/{node_id}')
node = response.json()
```

## Customization

### Styling

Modify the CSS in `hpo_frontend.html` to match your application's design:

```css
/* Change color scheme */
:root {
  --primary-color: #your-color;
  --secondary-color: #your-color;
  --accent-color: #your-color;
}

/* Modify node colors in JavaScript */
const colors = {
    selected: { background: '#your-color', border: '#your-color' },
    parent: { background: '#your-color', border: '#your-color' },
    child: { background: '#your-color', border: '#your-color' },
    default: { background: '#your-color', border: '#your-color' }
};
```

### Layout Options

```javascript
// Change visualization layout
const options = {
    layout: {
        hierarchical: {
            direction: 'UD', // Up-Down instead of Down-Up
            sortMethod: 'directed',
            levelSeparation: 150, // Increase spacing
            nodeSpacing: 100
        }
    }
};
```

### Search Configuration

```python
# Modify search behavior in backend
@app.get("/api/search")
async def search_hpo_terms(
    q: str = Query(..., min_length=1),  # Allow single character search
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)  # Increase max results
):
    # Custom search implementation
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure CORS is properly configured in the backend
2. **vis.js Not Loading**: Check CDN availability or use local file
3. **Large Data Performance**: Consider pagination and depth limiting
4. **Memory Issues**: Monitor backend memory usage with large datasets

### Debug Mode

```python
# Enable debug mode in backend
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug endpoints
@app.get("/api/debug/stats")
async def debug_stats():
    return {
        "nodes_loaded": len(nodes),
        "edges_loaded": len(edges),
        "memory_usage": "Add memory monitoring here"
    }
```

### Performance Monitoring

```python
# Add performance monitoring
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

@app.get("/api/search")
@monitor_performance
async def search_hpo_terms(...):
    # Implementation
```

This integration guide provides comprehensive instructions for integrating the HPO Tree Visualizer into any existing project, with examples for popular frameworks and customization options.
