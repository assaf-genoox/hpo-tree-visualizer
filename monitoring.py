# Simple monitoring script for production
import psutil
import time
import requests
from datetime import datetime

def check_system_health():
    """Check system resources and API health"""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "api_health": "unknown"
    }
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        health_status["api_health"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health_status["api_health"] = "unreachable"
    
    return health_status

def log_health():
    """Log health status to file"""
    health = check_system_health()
    with open("/var/log/hpo-visualizer-health.log", "a") as f:
        f.write(f"{health}\n")

if __name__ == "__main__":
    log_health()
