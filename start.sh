#!/bin/bash

# Start the FastAPI backend in the background
uvicorn hpo_backend:app --host 0.0.0.0 --port 8000 &

# Wait a moment for the backend to start
sleep 5

# Start nginx in the foreground
nginx -g "daemon off;"
