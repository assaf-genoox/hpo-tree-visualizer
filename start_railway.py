#!/usr/bin/env python3
"""
Railway startup script for HPO Tree Visualizer
This ensures the app starts correctly on Railway
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the HPO Tree Visualizer on Railway"""
    
    # Get port from Railway environment variable
    port = os.getenv("PORT", "8000")
    host = "0.0.0.0"
    
    print(f"🚀 Starting HPO Tree Visualizer on {host}:{port}")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Check if hp.json exists
    if not Path("hp.json").exists():
        print("❌ Error: hp.json not found!")
        print("Please ensure the HPO data file is included in your deployment")
        sys.exit(1)
    
    # Start the FastAPI application
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "hpo_backend:app", 
            "--host", host, 
            "--port", port,
            "--workers", "1"  # Single worker for Railway
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down HPO Tree Visualizer...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
