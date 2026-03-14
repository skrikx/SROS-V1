import subprocess
import sys
import time
import os
import signal
import webbrowser

def start_nexus():
    """Start SROS Nexus (Backend + Frontend)."""
    print(">>> Initializing SROS Nexus Sequence...")
    
    # Load .env file
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        print(f">>> Loading environment from {env_path}")
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip()
    else:
        print(">>> WARNING: No .env file found!")

    # 1. Start Backend
    print(">>> Launching SROS API Kernel (Port 8001)...")
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = os.getcwd()
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "sros.nexus.cli.main", "dashboard", "serve"],
        cwd=os.getcwd(),
        env=backend_env,
        shell=False
    )
    
    # Wait for backend to warm up
    time.sleep(3)
    
    # 2. Start Frontend
    print(">>> Launching Nexus UI (Port 3000)...")
    frontend_dir = os.path.join(os.getcwd(), "sros", "apps", "sros_web_nexus", "ui")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )
    
    print(">>> SROS Nexus Online.")
    print(">>> Access UI: http://localhost:3000")
    print(">>> Press Ctrl+C to terminate.")
    
    # Open Browser
    time.sleep(2)
    webbrowser.open("http://localhost:3000")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n>>> Terminating SROS Nexus...")
        backend_process.terminate()
        # Frontend is shell=True, so we might need stronger kill if on Windows
        if sys.platform == 'win32':
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(frontend_process.pid)])
        else:
            frontend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    start_nexus()
