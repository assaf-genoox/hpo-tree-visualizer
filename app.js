// HPO Tree Visualizer Application
class HPOExplorer {
    constructor() {
        this.hpoData = null;
        this.nodes = new Map();
        this.edges = [];
        this.network = null;
        this.currentDepth = 2;
        this.selectedNode = null;
        this.visNodes = null;
        this.visEdges = null;
        
        this.init();
    }
    
    async init() {
        this.showLoading(true);
        
        // Wait a bit for vis.js to fully load
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Check if vis.js is loaded
        if (typeof vis === 'undefined' || !vis.Network) {
            console.error('vis.js library not loaded initially, waiting more...');
            // Wait a bit more and try again
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            if (typeof vis === 'undefined' || !vis.Network) {
                console.error('vis.js library still not loaded!');
                this.showLoading(false);
                document.getElementById('networkVisualization').innerHTML = 
                    '<div style="padding: 50px; text-align: center; color: #d63031;">' +
                    'Error: Visualization library failed to load.<br>' +
                    'Please refresh the page (Ctrl+R or Cmd+R).' +
                    '</div>';
                return;
            }
        }
        
        console.log('vis.js loaded successfully');
        await this.initializeApp();
    }
    
    async initializeApp() {
        await this.loadHPOData();
        this.processData();
        this.setupEventListeners();
        this.initializeVisualization();
        this.updateStats();
        this.showLoading(false);
    }
    
    async loadHPOData() {
        try {
            const response = await fetch('hp.json');
            const data = await response.json();
            this.hpoData = data.graphs[0];
            console.log('HPO data loaded successfully');
        } catch (error) {
            console.error('Error loading HPO data:', error);
            alert('Error loading HPO data. Please check the console for details.');
        }
    }
    
    processData() {
        // Process nodes
        this.hpoData.nodes.forEach(node => {
            const processedNode = {
                id: node.id,
                label: node.lbl || 'Unknown',
                fullId: node.id.replace('http://purl.obolibrary.org/obo/', ''),
                definition: node.meta?.definition?.val || '',
                synonyms: node.meta?.synonyms?.map(s => s.val) || [],
                xrefs: node.meta?.xrefs?.map(x => x.val) || [],
                comments: node.meta?.comments || []
            };
            this.nodes.set(node.id, processedNode);
        });
        
        // Process edges
        this.edges = this.hpoData.edges.filter(edge => edge.pred === 'is_a').map(edge => ({
            from: edge.sub,
            to: edge.obj,
            arrows: 'to'
        }));
        
        // Build parent-child relationships
        this.nodes.forEach(node => {
            node.parents = [];
            node.children = [];
        });
        
        this.edges.forEach(edge => {
            const childNode = this.nodes.get(edge.from);
            const parentNode = this.nodes.get(edge.to);
            
            if (childNode && parentNode) {
                childNode.parents.push(parentNode.id);
                parentNode.children.push(childNode.id);
            }
        });
    }
    
    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const clearBtn = document.getElementById('clearBtn');
        const autocompleteList = document.getElementById('autocompleteList');
        
        searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
            clearBtn.style.display = e.target.value ? 'block' : 'none';
        });
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
        
        searchBtn.addEventListener('click', () => this.performSearch());
        
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            clearBtn.style.display = 'none';
            autocompleteList.style.display = 'none';
            autocompleteList.innerHTML = '';
        });
        
        // Click outside to close autocomplete
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-section')) {
                autocompleteList.style.display = 'none';
            }
        });
        
        // Depth slider
        const depthSlider = document.getElementById('depthSlider');
        const depthValue = document.getElementById('depthValue');
        
        depthSlider.addEventListener('input', (e) => {
            this.currentDepth = parseInt(e.target.value);
            depthValue.textContent = this.currentDepth;
            if (this.selectedNode) {
                this.updateVisualization(this.selectedNode);
            }
        });
        
        // Control buttons
        document.getElementById('resetViewBtn').addEventListener('click', () => {
            if (this.network) {
                this.network.fit();
            }
        });
        
        document.getElementById('expandBtn').addEventListener('click', () => {
            if (this.selectedNode) {
                const currentSliderValue = document.getElementById('depthSlider').value;
                const newValue = Math.min(5, parseInt(currentSliderValue) + 1);
                document.getElementById('depthSlider').value = newValue;
                document.getElementById('depthValue').textContent = newValue;
                this.currentDepth = newValue;
                this.updateVisualization(this.selectedNode);
            }
        });
    }
    
    handleSearchInput(query) {
        const autocompleteList = document.getElementById('autocompleteList');
        
        if (query.length < 2) {
            autocompleteList.style.display = 'none';
            return;
        }
        
        const matches = this.searchNodes(query);
        
        if (matches.length === 0) {
            autocompleteList.style.display = 'none';
            return;
        }
        
        autocompleteList.innerHTML = '';
        matches.slice(0, 10).forEach(node => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
                ${node.label}
                <span class="term-id">${node.fullId}</span>
            `;
            item.addEventListener('click', () => {
                this.selectNode(node.id);
                document.getElementById('searchInput').value = node.label;
                autocompleteList.style.display = 'none';
            });
            autocompleteList.appendChild(item);
        });
        
        autocompleteList.style.display = 'block';
    }
    
    searchNodes(query) {
        const lowerQuery = query.toLowerCase();
        const results = [];
        
        this.nodes.forEach(node => {
            if (
                node.label.toLowerCase().includes(lowerQuery) ||
                node.fullId.toLowerCase().includes(lowerQuery) ||
                node.synonyms.some(syn => syn.toLowerCase().includes(lowerQuery))
            ) {
                results.push(node);
            }
        });
        
        // Sort by relevance (exact matches first, then by label length)
        results.sort((a, b) => {
            const aExact = a.label.toLowerCase() === lowerQuery || a.fullId.toLowerCase() === lowerQuery;
            const bExact = b.label.toLowerCase() === lowerQuery || b.fullId.toLowerCase() === lowerQuery;
            
            if (aExact && !bExact) return -1;
            if (!aExact && bExact) return 1;
            
            return a.label.length - b.label.length;
        });
        
        return results;
    }
    
    performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) return;
        
        const matches = this.searchNodes(query);
        if (matches.length > 0) {
            this.selectNode(matches[0].id);
        } else {
            alert('No matching HPO terms found.');
        }
        
        document.getElementById('autocompleteList').style.display = 'none';
    }
    
    selectNode(nodeId) {
        this.selectedNode = nodeId;
        this.updateSelectedTermInfo();
        this.updateRelationshipsDisplay();
        this.updateVisualization(nodeId);
    }
    
    updateSelectedTermInfo() {
        const infoDiv = document.getElementById('selectedTermInfo');
        const node = this.nodes.get(this.selectedNode);
        
        if (!node) {
            infoDiv.innerHTML = '<p class="placeholder">Select a term to view details</p>';
            return;
        }
        
        let html = `
            <div class="term-id">${node.fullId}</div>
            <div class="term-label">${node.label}</div>
        `;
        
        if (node.definition) {
            html += `<div class="term-definition">${node.definition}</div>`;
        }
        
        if (node.synonyms.length > 0) {
            html += `
                <div style="margin-top: 15px;">
                    <strong>Synonyms:</strong>
                    <ul style="margin-left: 20px; margin-top: 5px;">
                        ${node.synonyms.map(syn => `<li>${syn}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        infoDiv.innerHTML = html;
    }
    
    updateRelationshipsDisplay() {
        const node = this.nodes.get(this.selectedNode);
        
        if (!node) {
            document.getElementById('parentsList').innerHTML = '<p class="placeholder">No term selected</p>';
            document.getElementById('childrenList').innerHTML = '<p class="placeholder">No term selected</p>';
            return;
        }
        
        // Display parents
        const parentsHtml = node.parents.length > 0
            ? node.parents.map(parentId => {
                const parent = this.nodes.get(parentId);
                return `
                    <div class="relation-item" onclick="hpoExplorer.selectNode('${parentId}')">
                        <div class="item-label">${parent.label}</div>
                        <div class="item-id">${parent.fullId}</div>
                    </div>
                `;
            }).join('')
            : '<p class="placeholder">No parent terms</p>';
        
        document.getElementById('parentsList').innerHTML = parentsHtml;
        
        // Display children
        const childrenHtml = node.children.length > 0
            ? node.children.slice(0, 50).map(childId => {
                const child = this.nodes.get(childId);
                return `
                    <div class="relation-item" onclick="hpoExplorer.selectNode('${childId}')">
                        <div class="item-label">${child.label}</div>
                        <div class="item-id">${child.fullId}</div>
                    </div>
                `;
            }).join('') + (node.children.length > 50 ? `<p class="placeholder">... and ${node.children.length - 50} more</p>` : '')
            : '<p class="placeholder">No child terms</p>';
        
        document.getElementById('childrenList').innerHTML = childrenHtml;
    }
    
    initializeVisualization() {
        const container = document.getElementById('networkVisualization');
        
        if (!container) {
            console.error('Network visualization container not found!');
            return;
        }
        
        // Create initial data with just the root node
        const rootId = 'http://purl.obolibrary.org/obo/HP_0000001';
        const rootNode = this.nodes.get(rootId);
        
        if (!rootNode) {
            console.error('Root node not found in data!');
            return;
        }
        
        console.log('Initializing visualization with root node:', rootNode);
        
        // Use plain arrays initially, convert to DataSet if available
        const initialNodes = [{
            id: rootId,
            label: this.formatNodeLabel(rootNode.label),
            title: `${rootNode.fullId}\n${rootNode.label}`,
            color: {
                background: '#4a90e2',
                border: '#3a7bc8',
                highlight: {
                    background: '#6c5ce7',
                    border: '#5f3dc4'
                }
            },
            font: {
                color: 'white'
            }
        }];
        
        const initialEdges = [];
        
        // Check if DataSet is available
        if (vis.DataSet) {
            this.visNodes = new vis.DataSet(initialNodes);
            this.visEdges = new vis.DataSet(initialEdges);
        } else {
            console.warn('vis.DataSet not available, using arrays');
            this.visNodes = initialNodes;
            this.visEdges = initialEdges;
        }
        
        const data = {
            nodes: this.visNodes,
            edges: this.visEdges
        };
        
        const options = {
            nodes: {
                shape: 'box',
                margin: 10,
                widthConstraint: {
                    maximum: 200
                },
                font: {
                    size: 14,
                    face: 'Arial'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                },
                smooth: {
                    type: 'cubicBezier',
                    roundness: 0.4
                },
                width: 2,
                color: {
                    color: '#848484',
                    highlight: '#4a90e2'
                }
            },
            layout: {
                hierarchical: {
                    direction: 'UD',
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
            },
            interaction: {
                dragNodes: true,
                dragView: true,
                zoomView: true,
                hover: true
            }
        };
        
        try {
            this.network = new vis.Network(container, data, options);
            
            console.log('Network created successfully');
            
            // Handle node clicks
            this.network.on('click', (params) => {
                if (params.nodes.length > 0) {
                    this.selectNode(params.nodes[0]);
                }
            });
            
            // Handle double clicks for expansion
            this.network.on('doubleClick', (params) => {
                if (params.nodes.length > 0) {
                    this.expandNode(params.nodes[0]);
                }
            });
            
            // Wait for network to stabilize before selecting root
            this.network.once('stabilizationIterationsDone', () => {
                console.log('Network stabilized');
                this.selectNode(rootId);
            });
            
            // Also select root immediately
            this.selectNode(rootId);
            
        } catch (error) {
            console.error('Error creating network visualization:', error);
            container.innerHTML = '<div style="padding: 50px; text-align: center; color: #d63031;">Error creating visualization. Please refresh the page.</div>';
        }
    }
    
    updateVisualization(centerNodeId) {
        const subgraph = this.getSubgraph(centerNodeId, this.currentDepth);
        
        // Update nodes
        const nodesToAdd = [];
        const nodesToUpdate = [];
        
        // Handle both DataSet and array cases
        let existingNodeIds;
        if (this.visNodes.getIds) {
            existingNodeIds = new Set(this.visNodes.getIds());
        } else {
            existingNodeIds = new Set(this.visNodes.map(n => n.id));
        }
        
        subgraph.nodes.forEach(node => {
            const nodeData = {
                id: node.id,
                label: this.formatNodeLabel(node.label),
                title: `${node.fullId}\n${node.label}${node.definition ? '\n\n' + node.definition.substring(0, 200) + '...' : ''}`,
                level: node.level
            };
            
            // Color based on relationship to selected node
            if (node.id === centerNodeId) {
                nodeData.color = {
                    background: '#6c5ce7',
                    border: '#5f3dc4',
                    highlight: {
                        background: '#a29bfe',
                        border: '#6c5ce7'
                    }
                };
                nodeData.font = { color: 'white' };
            } else if (node.isParent) {
                nodeData.color = {
                    background: '#00b894',
                    border: '#00896e',
                    highlight: {
                        background: '#55efc4',
                        border: '#00b894'
                    }
                };
                nodeData.font = { color: 'white' };
            } else if (node.isChild) {
                nodeData.color = {
                    background: '#4a90e2',
                    border: '#3a7bc8',
                    highlight: {
                        background: '#74b9ff',
                        border: '#4a90e2'
                    }
                };
                nodeData.font = { color: 'white' };
            } else {
                nodeData.color = {
                    background: '#dfe6e9',
                    border: '#b2bec3',
                    highlight: {
                        background: '#74b9ff',
                        border: '#4a90e2'
                    }
                };
                nodeData.font = { color: '#2c3e50' };
            }
            
            if (existingNodeIds.has(node.id)) {
                nodesToUpdate.push(nodeData);
            } else {
                nodesToAdd.push(nodeData);
            }
        });
        
        // Remove nodes not in subgraph
        const subgraphNodeIds = new Set(subgraph.nodes.map(n => n.id));
        const nodesToRemove = Array.from(existingNodeIds).filter(id => !subgraphNodeIds.has(id));
        
        // Update edges
        const newEdges = subgraph.edges.map(edge => ({
            id: `${edge.from}-${edge.to}`,
            from: edge.from,
            to: edge.to,
            arrows: 'to'
        }));
        
        // Apply changes - handle both DataSet and array cases
        if (this.visNodes.remove) {
            // DataSet methods
            this.visNodes.remove(nodesToRemove);
            this.visNodes.add(nodesToAdd);
            this.visNodes.update(nodesToUpdate);
            
            this.visEdges.clear();
            this.visEdges.add(newEdges);
        } else {
            // Array fallback - recreate the arrays
            const currentNodes = Array.isArray(this.visNodes) ? this.visNodes : [];
            const filteredNodes = currentNodes.filter(n => !nodesToRemove.includes(n.id));
            const updatedNodes = filteredNodes.map(n => {
                const update = nodesToUpdate.find(u => u.id === n.id);
                return update || n;
            });
            this.visNodes = [...updatedNodes, ...nodesToAdd];
            this.visEdges = newEdges;
            
            // Update the network data
            if (this.network) {
                this.network.setData({
                    nodes: this.visNodes,
                    edges: this.visEdges
                });
            }
        }
        
        // Update visible nodes count
        document.getElementById('visibleNodes').textContent = subgraph.nodes.length;
        
        // Fit network to view after a short delay
        setTimeout(() => {
            this.network.fit({
                animation: {
                    duration: 500,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }, 100);
    }
    
    getSubgraph(centerNodeId, depth) {
        const visited = new Set();
        const nodes = [];
        const edges = [];
        const centerNode = this.nodes.get(centerNodeId);
        
        if (!centerNode) return { nodes: [], edges: [] };
        
        // BFS to get nodes within depth
        const queue = [{ id: centerNodeId, level: 0, isParent: false, isChild: false }];
        visited.add(centerNodeId);
        
        while (queue.length > 0) {
            const current = queue.shift();
            const currentNode = this.nodes.get(current.id);
            
            nodes.push({
                ...currentNode,
                level: current.level,
                isParent: current.isParent,
                isChild: current.isChild
            });
            
            if (current.level < depth) {
                // Add parents
                currentNode.parents.forEach(parentId => {
                    if (!visited.has(parentId)) {
                        visited.add(parentId);
                        queue.push({
                            id: parentId,
                            level: current.level + 1,
                            isParent: current.id === centerNodeId,
                            isChild: false
                        });
                    }
                    edges.push({ from: current.id, to: parentId });
                });
                
                // Add children
                currentNode.children.forEach(childId => {
                    if (!visited.has(childId)) {
                        visited.add(childId);
                        queue.push({
                            id: childId,
                            level: current.level + 1,
                            isParent: false,
                            isChild: current.id === centerNodeId
                        });
                    }
                    edges.push({ from: childId, to: current.id });
                });
            }
        }
        
        return { nodes, edges };
    }
    
    expandNode(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return;
        
        // Add immediate children if not already visible
        let existingNodeIds;
        if (this.visNodes.getIds) {
            existingNodeIds = new Set(this.visNodes.getIds());
        } else {
            existingNodeIds = new Set(this.visNodes.map(n => n.id));
        }
        const nodesToAdd = [];
        const edgesToAdd = [];
        
        node.children.slice(0, 10).forEach(childId => {
            if (!existingNodeIds.has(childId)) {
                const child = this.nodes.get(childId);
                nodesToAdd.push({
                    id: childId,
                    label: this.formatNodeLabel(child.label),
                    title: `${child.fullId}\n${child.label}`,
                    color: {
                        background: '#4a90e2',
                        border: '#3a7bc8',
                        highlight: {
                            background: '#74b9ff',
                            border: '#4a90e2'
                        }
                    },
                    font: { color: 'white' }
                });
                edgesToAdd.push({
                    id: `${childId}-${nodeId}`,
                    from: childId,
                    to: nodeId,
                    arrows: 'to'
                });
            }
        });
        
        if (nodesToAdd.length > 0) {
            if (this.visNodes.add) {
                this.visNodes.add(nodesToAdd);
                this.visEdges.add(edgesToAdd);
                document.getElementById('visibleNodes').textContent = this.visNodes.length;
            } else {
                // Array fallback
                this.visNodes = [...this.visNodes, ...nodesToAdd];
                this.visEdges = [...this.visEdges, ...edgesToAdd];
                document.getElementById('visibleNodes').textContent = this.visNodes.length;
                
                // Update the network
                if (this.network) {
                    this.network.setData({
                        nodes: this.visNodes,
                        edges: this.visEdges
                    });
                }
            }
        }
    }
    
    formatNodeLabel(label) {
        // Truncate long labels for better visualization
        if (label.length > 30) {
            return label.substring(0, 27) + '...';
        }
        return label;
    }
    
    updateStats() {
        document.getElementById('totalTerms').textContent = this.nodes.size.toLocaleString();
        document.getElementById('totalRelations').textContent = this.edges.length.toLocaleString();
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// Initialize the application when the page loads
let hpoExplorer;

// Use both DOMContentLoaded and load to ensure everything is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    // DOMContentLoaded already fired
    initApp();
}

function initApp() {
    // Additional wait for external scripts
    window.addEventListener('load', () => {
        setTimeout(() => {
            console.log('Starting HPO Explorer initialization...');
            console.log('vis object available:', typeof vis !== 'undefined');
            if (typeof vis !== 'undefined') {
                console.log('vis.Network available:', typeof vis.Network);
                console.log('vis.DataSet available:', typeof vis.DataSet);
            }
            hpoExplorer = new HPOExplorer();
        }, 500);
    });
    
    // If window is already loaded, initialize immediately
    if (document.readyState === 'complete') {
        setTimeout(() => {
            console.log('Page already loaded, initializing...');
            console.log('vis object available:', typeof vis !== 'undefined');
            hpoExplorer = new HPOExplorer();
        }, 500);
    }
}
