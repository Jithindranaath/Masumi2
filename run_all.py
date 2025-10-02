#!/usr/bin/env python3
"""
Script to run the complete Web3 Compliance Analysis setup:
- Main API server (port 8000)
- Web3 Frontend (port 3000)
"""

import subprocess
import sys
import time
import signal
import os

def run_command(command, name):
    """Run a command in subprocess"""
    print(f"Starting {name}...")
    return subprocess.Popen(command, shell=True, cwd=os.getcwd())

def main():
    processes = []

    try:
        # Start main API server
        api_cmd = "python main.py api"
        api_process = run_command(api_cmd, "Main API Server")
        processes.append(("Main API", api_process))

        # Wait a bit for API to start
        time.sleep(3)

        # Start frontend
        frontend_cmd = "python web3_frontend.py"
        frontend_process = run_command(frontend_cmd, "Web3 Frontend")
        processes.append(("Web3 Frontend", frontend_process))

        print("\n" + "="*50)
        print("🚀 Web3 Compliance Analysis Setup Running!")
        print("="*50)
        print("📡 Main API: http://localhost:8000")
        print("🌐 Frontend: http://localhost:3000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("="*50)
        print("Press Ctrl+C to stop all services")
        print("="*50)

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Terminate all processes
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  {name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")

if __name__ == "__main__":
    # Check if required files exist
    required_files = ["main.py", "web3_frontend.py", "crew_definition.py", "agents/compliance_agents.py"]
    missing_files = [f for f in required_files if not os.path.exists(f)]

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        sys.exit(1)

    # Set TEST_MODE for easier testing
    os.environ["TEST_MODE"] = "true"
    print("🔧 TEST_MODE enabled for development")

    # Check if virtual environment is activated (optional)
    if not os.getenv("VIRTUAL_ENV"):
        print("⚠️  Warning: No virtual environment detected. Make sure dependencies are installed.")

    main()