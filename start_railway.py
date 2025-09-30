#!/usr/bin/env python3
"""
Railway startup script for HPO Tree Visualizer
This ensures the app starts correctly on Railway
"""

import os
import sys
import subprocess
import time
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
    
    print(f"📁 HPO data file found: {Path('hp.json').stat().st_size / (1024*1024):.1f} MB")
    
    # Start the FastAPI application with proper configuration
    try:
        print("🔄 Starting FastAPI server...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "hpo_backend:app", 
            "--host", host, 
            "--port", port,
            "--workers", "1",  # Single worker for Railway
            "--timeout-keep-alive", "30",
            "--timeout-graceful-shutdown", "30"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down HPO Tree Visualizer...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
