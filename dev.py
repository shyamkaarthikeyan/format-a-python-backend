#!/usr/bin/env python3
"""
Development server script for Format-A Python Backend
Provides local development utilities and testing
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not installed")
        return False

def install_vercel_cli():
    """Install Vercel CLI if not present"""
    print("📦 Installing Vercel CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
        print("✅ Vercel CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Vercel CLI")
        return False

def check_environment():
    """Check if environment variables are set up"""
    env_file = Path('.env.local')
    if env_file.exists():
        print("✅ .env.local found")
        return True
    else:
        print("⚠️  .env.local not found, using .env.example as template")
        if Path('.env.example').exists():
            print("📋 Copy .env.example to .env.local and configure your variables")
        return False

def start_dev_server(port=3001):
    """Start the Vercel development server"""
    print(f"🚀 Starting Python backend development server on port {port}...")
    
    # Set environment variables for development
    env = os.environ.copy()
    env['PORT'] = str(port)
    
    try:
        # Start vercel dev with specific port
        process = subprocess.Popen(
            ['vercel', 'dev', '--listen', str(port)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"📡 Server starting... (PID: {process.pid})")
        print(f"🌐 Local URL: http://localhost:{port}")
        print("📋 Available endpoints:")
        print(f"   - http://localhost:{port}/api/health-simple")
        print(f"   - http://localhost:{port}/api/health")
        print(f"   - http://localhost:{port}/api/document-generator")
        print("\n💡 Press Ctrl+C to stop the server\n")
        
        # Stream output
        for line in process.stdout:
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
        process.terminate()
        process.wait()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def test_endpoints(port=3001):
    """Test local endpoints"""
    base_url = f"http://localhost:{port}"
    endpoints = [
        "/api/health-simple",
        "/api/health",
        "/api/test-simple"
    ]
    
    print(f"🧪 Testing endpoints on {base_url}...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Connection failed: {e}")

def show_help():
    """Show help information"""
    print("🐍 Format-A Python Backend Development Server")
    print("=" * 50)
    print("Usage: python dev.py [command] [options]")
    print("")
    print("Commands:")
    print("  start [port]    Start development server (default: port 3001)")
    print("  test [port]     Test endpoints on running server")
    print("  check           Check prerequisites and environment")
    print("  help            Show this help message")
    print("")
    print("Examples:")
    print("  python dev.py                 # Start server on port 3001")
    print("  python dev.py start 3002      # Start server on port 3002")
    print("  python dev.py test            # Test endpoints on port 3001")
    print("  python dev.py check           # Check setup")
    print("")
    print("Environment:")
    print("  .env.local      Local environment variables")
    print("  .env.example    Template for environment setup")

def check_setup():
    """Check complete setup"""
    print("🔍 Checking Python Backend Setup")
    print("=" * 40)
    
    # Check Vercel CLI
    vercel_ok = check_vercel_cli()
    
    # Check environment
    env_ok = check_environment()
    
    # Check Python dependencies
    print("📦 Checking Python dependencies...")
    try:
        import docx
        import reportlab
        import psycopg2
        import jwt
        print("✅ All Python dependencies installed")
        deps_ok = True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        deps_ok = False
    
    # Check files
    required_files = [
        'requirements.txt',
        'vercel.json',
        '.env.example',
        'api/health.py',
        'api/document-generator.py'
    ]
    
    print("📁 Checking required files...")
    files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            files_ok = False
    
    # Overall status
    print("\n" + "=" * 40)
    if all([vercel_ok, env_ok, deps_ok, files_ok]):
        print("✅ Setup complete - ready for development!")
        return True
    else:
        print("❌ Setup incomplete - fix issues above")
        return False

def main():
    """Main development script"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ["help", "--help", "-h"]:
            show_help()
            return
        elif command == "check":
            check_setup()
            return
        elif command == "test":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 3001
            test_endpoints(port)
            return
        elif command == "start":
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 3001
        else:
            print(f"Unknown command: {command}")
            show_help()
            return
    else:
        # Default: start development server
        port = 3001
    
    print("🐍 Format-A Python Backend Development Server")
    print("=" * 50)
    
    # Check prerequisites
    if not check_vercel_cli():
        if not install_vercel_cli():
            print("❌ Cannot proceed without Vercel CLI")
            sys.exit(1)
    
    check_environment()
    start_dev_server(port)

if __name__ == "__main__":
    main()