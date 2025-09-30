# Production configuration for HPO Visualizer
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

def create_production_app():
    app = FastAPI(
        title="HPO Tree Visualizer API",
        version="1.0.0",
        docs_url="/api/docs" if os.getenv("ENVIRONMENT") == "development" else None,
        redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") == "development" else None
    )
    
    # CORS configuration for production
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    # Serve static files (frontend)
    app.mount("/", StaticFiles(directory=".", html=True), name="static")
    
    return app

# Environment variables for production
# ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
# ENVIRONMENT=production
# HPO_DATA_PATH=/app/hp.json
