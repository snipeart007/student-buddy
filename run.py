import os
import subprocess
import time
import webbrowser
import sys

def start_backend():
    print("Starting backend server...")
    # Use uv to run the backend in the correct environment
    cmd = ["uv", "run", "--project", "backend", "python", "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"]
    process = subprocess.Popen(cmd)
    return process

def open_browser():
    print("Opening browser...")
    time.sleep(3) # Wait for server to start
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Ensure dependencies are installed (optional, but good for local app)
    # subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
    
    backend_process = start_backend()
    
    try:
        open_browser()
        backend_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        backend_process.terminate()
