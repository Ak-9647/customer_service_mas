#!/usr/bin/env python3
"""
ADK Application Startup Script
Starts both backend and frontend services with proper error handling
"""

import subprocess
import time
import sys
import os
import signal
import requests
from pathlib import Path

def print_banner():
    print("🎯 ADK Application - Complete Startup")
    print("=" * 50)

def check_requirements():
    """Check if required files exist"""
    print("🔍 Checking requirements...")
    
    # Check if virtual environment exists
    if not Path(".venv").exists():
        print("❌ Virtual environment not found. Please run: python -m venv .venv")
        return False
    
    # Check if frontend directory exists
    if not Path("frontend").exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found")
        return False
    
    print("✅ Requirements check passed")
    return True

def kill_existing_processes():
    """Kill any existing processes on our ports"""
    print("🧹 Cleaning up existing processes...")
    
    # Kill processes on port 8080 (backend)
    try:
        result = subprocess.run(["lsof", "-ti:8080"], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(["kill", "-9", pid], capture_output=True)
            print(f"🧹 Killed {len(pids)} process(es) on port 8080")
    except Exception as e:
        pass  # Ignore errors if no processes found
    
    # Kill processes on port 5173 (frontend)
    try:
        result = subprocess.run(["lsof", "-ti:5173"], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(["kill", "-9", pid], capture_output=True)
            print(f"🧹 Killed {len(pids)} process(es) on port 5173")
    except Exception as e:
        pass  # Ignore errors if no processes found

def wait_for_backend():
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to start...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8080/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is running and healthy")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            time.sleep(1)
    
    print("❌ Backend failed to start within 30 seconds")
    return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend...")
    
    # Activate virtual environment and start backend
    env = os.environ.copy()
    env["PATH"] = f"{os.path.abspath('.venv/bin')}:{env['PATH']}"
    
    backend_process = subprocess.Popen(
        ["python", "main.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return backend_process

def start_frontend():
    """Start the frontend server"""
    print("🚀 Starting Frontend...")
    
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return frontend_process

def print_success_info():
    """Print success information"""
    print("=" * 50)
    print("✅ ADK Application is running!")
    print("📍 Backend API: http://localhost:8080")
    print("📍 Frontend UI: http://localhost:5173")
    print("📍 API Documentation: http://localhost:8080/docs")
    print("📍 Health Check: http://localhost:8080/health")
    print()
    print("💡 Try these test messages:")
    print("   - 'Check order 12345'")
    print("   - 'I want a refund for order 12345'")
    print("   - 'What is the status of my order?'")
    print()
    print("🛑 Press Ctrl+C to stop all services")
    print("=" * 50)

def monitor_processes(backend_process, frontend_process):
    """Monitor both processes and handle output"""
    try:
        while True:
            # Check if backend is still running
            if backend_process.poll() is not None:
                print("❌ Backend process died!")
                return False
            
            # Check if frontend is still running
            if frontend_process.poll() is not None:
                print("❌ Frontend process died!")
                return False
            
            # Read and display output from backend
            if backend_process.stdout.readable():
                line = backend_process.stdout.readline()
                if line:
                    print(f"[Backend] {line.rstrip()}")
            
            # Read and display output from frontend
            if frontend_process.stdout.readable():
                line = frontend_process.stdout.readline()
                if line:
                    print(f"[Frontend] {line.rstrip()}")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        return True

def cleanup_processes(backend_process, frontend_process):
    """Clean up processes"""
    print("   Stopping Backend...")
    if backend_process and backend_process.poll() is None:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
    
    print("   Stopping Frontend...")
    if frontend_process and frontend_process.poll() is None:
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
    
    print("✅ All services stopped")

def main():
    """Main function"""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    # Clean up any existing processes
    kill_existing_processes()
    
    # Start backend
    backend_process = start_backend()
    
    # Wait for backend to be ready
    if not wait_for_backend():
        cleanup_processes(backend_process, None)
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    
    # Give frontend a moment to start
    time.sleep(3)
    
    # Print success information
    print_success_info()
    
    # Monitor processes
    try:
        monitor_processes(backend_process, frontend_process)
    finally:
        cleanup_processes(backend_process, frontend_process)

if __name__ == "__main__":
    main() 