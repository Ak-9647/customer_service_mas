#!/usr/bin/env python3
"""
Local development startup script for ADK application
"""
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def run_command(cmd, name, cwd=None):
    """Run a command in a subprocess"""
    print(f"🚀 Starting {name}...")
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        def print_output():
            for line in iter(process.stdout.readline, ''):
                print(f"[{name}] {line.rstrip()}")
        
        thread = threading.Thread(target=print_output)
        thread.daemon = True
        thread.start()
        
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("🎯 Starting ADK Application Locally")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment")
        print("   Consider running: python -m venv .venv && source .venv/bin/activate")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Creating template...")
        with open('.env', 'w') as f:
            f.write("""# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Database URLs (using mock connections by default)
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://user:password@localhost:5432/adk_db
MONGODB_URL=mongodb://localhost:27017/adk_db

# Server Configuration
HOST=0.0.0.0
PORT=8080
""")
        print("✅ Created .env template. Please add your API keys!")
    
    processes = []
    
    try:
        # Start the main ADK application
        main_process = run_command(
            "python main.py",
            "ADK Main App",
            cwd="."
        )
        if main_process:
            processes.append(("ADK Main App", main_process))
        
        # Wait a bit for the main app to start
        time.sleep(3)
        
        # Start frontend (in a separate terminal or background)
        print("\n🌐 To start the frontend, run in another terminal:")
        print("   cd frontend && npm run dev")
        print("   Or: cd frontend && npx vite")
        
        print("\n✅ ADK Application is running!")
        print("📍 Backend: http://localhost:8080")
        print("📍 Frontend: http://localhost:5173 (after starting)")
        print("📍 API Docs: http://localhost:8080/docs")
        print("\n🛑 Press Ctrl+C to stop all services")
        
        # Keep the main process running
        if processes:
            main_process = processes[0][1]
            main_process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        for name, process in processes:
            print(f"   Stopping {name}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ All services stopped")

if __name__ == "__main__":
    main() 