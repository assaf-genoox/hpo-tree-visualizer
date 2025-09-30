# HPO Tree Visualizer

A high-performance web application for exploring the Human Phenotype Ontology (HPO) with interactive tree visualization, real-time search, and on-demand data loading.

## Features

- 🔍 **Real-time Search**: Search through 19,778+ HPO terms with autocomplete
- 🌳 **Interactive Tree Visualization**: Explore parent-child relationships with vis.js
- ⚡ **High Performance**: On-demand data loading prevents browser slowdowns
- 🎨 **Modern UI**: Clean, responsive design with color-coded nodes
- 🔗 **RESTful API**: Easy integration with existing applications
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices

## Quick Start

### Prerequisites

- Python 3.9+
- HPO JSON data file (`hp.json`)
- Modern web browser

### Installation

1. **Clone or download the files**
2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Place your HPO data file as `hp.json`**
   - Download from: https://hpo.jax.org/app/download/ontology
4. **Start the backend server**
   ```bash
   python hpo_backend.py
   ```
5. **Open the frontend**
   - Open `hpo_frontend.html` in your web browser
   - Or serve it: `python -m http.server 8080`

## Files Included

- `hpo_backend.py` - FastAPI backend server
- `hpo_frontend.html` - Complete web interface
- `requirements.txt` - Python dependencies
- `HPO_ARCHITECTURE_DOCUMENTATION.md` - Detailed technical documentation
- `INTEGRATION_GUIDE.md` - Integration instructions for other projects

## Usage

1. **Search**: Type in the search box to find HPO terms
2. **Explore**: Click on nodes to navigate the hierarchy
3. **Adjust Depth**: Use the slider to control visualization depth
4. **View Details**: See definitions, synonyms, and relationships in the sidebar

## API Endpoints

- `GET /api/stats` - Get HPO statistics
- `GET /api/search?q=query` - Search HPO terms
- `GET /api/node/{node_id}` - Get node details
- `GET /api/subgraph/{node_id}?depth=N` - Get subgraph for visualization
- `GET /api/node/{node_id}/parents` - Get parent terms
- `GET /api/node/{node_id}/children` - Get child terms

## Integration

See `INTEGRATION_GUIDE.md` for detailed instructions on integrating this component into existing applications (React, Vue, Angular, etc.).

## Architecture

- **Backend**: FastAPI with in-memory data structures for fast lookups
- **Frontend**: Vanilla JavaScript with vis.js for visualization
- **Data**: Processes HPO JSON into optimized parent-child relationships
- **Performance**: On-demand loading and pagination for large datasets

## Configuration

### Backend
- Modify `API_BASE_URL` in `hpo_frontend.html` to point to your backend
- Adjust CORS settings in `hpo_backend.py` for production

### Frontend
- Customize colors, layout, and styling in the HTML file
- Modify search behavior and visualization options

## Troubleshooting

- **CORS Issues**: Ensure backend CORS is configured for your domain
- **vis.js Loading**: Check CDN availability or use local file
- **Performance**: Reduce depth or implement pagination for large datasets
- **Data Loading**: Ensure `hp.json` is in the correct location

## License

This project is provided as-is for educational and research purposes.

## Support

For issues and questions, refer to the detailed documentation files included in this package.