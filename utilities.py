#!/usr/bin/env python3
"""
LangGraph Flow - Utilities Script
Combines testing, validation, and utility functions
"""

import os
import sys
import time
import httpx
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Try to import optional dependencies
try:
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Configuration from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3001")


class Colors:
    """Terminal colors"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def log(message: str, level: str = "INFO", color: str = None):
    """Log a message with timestamp and color"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if color:
        print(f"{color}[{timestamp}] [{level}] {message}{Colors.NC}")
    else:
        print(f"[{timestamp}] [{level}] {message}")


class SetupChecker:
    """Check if all required files and services are properly set up"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def check_directory_structure(self) -> bool:
        """Check if required directories exist"""
        log("Checking directory structure...", color=Colors.BLUE)
        
        required_dirs = [
            "airflow/dags",
            "airflow/plugins",
            "backend/api",
            "backend/core",
            "docker",
            "database/migrations",
            "frontend/src/components"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            if os.path.isdir(dir_path):
                log(f"  ✅ {dir_path}", color=Colors.GREEN)
            else:
                log(f"  ❌ {dir_path}", "ERROR", Colors.RED)
                self.errors.append(f"Missing directory: {dir_path}")
                all_exist = False
        
        return all_exist
    
    def check_required_files(self) -> bool:
        """Check if required files exist"""
        log("\nChecking required files...", color=Colors.BLUE)
        
        required_files = {
            "docker/docker-compose.yml": "Docker Compose configuration",
            ".env": "Environment configuration",
            "setup.sh": "Main setup script"
        }
        
        # Optional but recommended files
        optional_files = {
            "airflow/dags/visual_ai_workflow_dag.py": "Airflow DAG for workflows",
            "backend/api/workflow_triggers.py": "API endpoints",
            "requirements.txt": "Python dependencies"
        }
        
        all_required = True
        for file_path, description in required_files.items():
            if os.path.isfile(file_path):
                log(f"  ✅ {file_path}", color=Colors.GREEN)
            else:
                log(f"  ❌ {file_path} - {description}", "ERROR", Colors.RED)
                self.errors.append(f"Missing required file: {file_path}")
                all_required = False
        
        for file_path, description in optional_files.items():
            if os.path.isfile(file_path):
                log(f"  ✅ {file_path}", color=Colors.GREEN)
            else:
                log(f"  ⚠️  {file_path} - {description}", "WARNING", Colors.YELLOW)
                self.warnings.append(f"Missing optional file: {file_path}")
        
        return all_required
    
    def check_environment(self) -> bool:
        """Check environment configuration"""
        log("\nChecking environment configuration...", color=Colors.BLUE)
        
        if not os.path.exists(".env"):
            log("  ❌ .env file not found", "ERROR", Colors.RED)
            self.errors.append("No .env file found")
            return False
        
        required_vars = [
            "OPENAI_API_KEY",
            "LANGFUSE_SECRET_KEY",
            "LANGFUSE_PUBLIC_KEY",
            "AIRFLOW_UID"
        ]
        
        # Load .env file
        env_vars = {}
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
        
        all_set = True
        for var in required_vars:
            if var in env_vars:
                if env_vars[var].startswith("your_") or env_vars[var] == "":
                    log(f"  ⚠️  {var} - needs to be configured", "WARNING", Colors.YELLOW)
                    self.warnings.append(f"{var} needs to be configured")
                else:
                    log(f"  ✅ {var}", color=Colors.GREEN)
            else:
                log(f"  ❌ {var} - not found", "ERROR", Colors.RED)
                self.errors.append(f"Missing environment variable: {var}")
                all_set = False
        
        return all_set
    
    def check_docker(self) -> bool:
        """Check Docker availability"""
        log("\nChecking Docker...", color=Colors.BLUE)
        
        # Check Docker command
        try:
            import subprocess
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                log(f"  ✅ Docker installed: {result.stdout.strip()}", color=Colors.GREEN)
            else:
                raise Exception("Docker command failed")
        except Exception as e:
            log("  ❌ Docker not found", "ERROR", Colors.RED)
            self.errors.append("Docker is not installed")
            return False
        
        # Check Docker daemon
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                log("  ✅ Docker daemon is running", color=Colors.GREEN)
            else:
                raise Exception("Docker daemon not running")
        except Exception as e:
            log("  ❌ Docker daemon is not running", "ERROR", Colors.RED)
            self.errors.append("Docker daemon is not running")
            return False
        
        return True
    
    def generate_report(self):
        """Generate setup check report"""
        log("\n" + "="*60, color=Colors.BLUE)
        log("Setup Check Summary", color=Colors.BLUE)
        log("="*60, color=Colors.BLUE)
        
        if not self.errors and not self.warnings:
            log("\n✅ All checks passed! Your setup is ready.", color=Colors.GREEN)
        else:
            if self.errors:
                log(f"\n❌ Found {len(self.errors)} errors:", "ERROR", Colors.RED)
                for error in self.errors:
                    log(f"  - {error}", "ERROR", Colors.RED)
            
            if self.warnings:
                log(f"\n⚠️  Found {len(self.warnings)} warnings:", "WARNING", Colors.YELLOW)
                for warning in self.warnings:
                    log(f"  - {warning}", "WARNING", Colors.YELLOW)
            
            log("\nPlease fix the issues above before starting services.", color=Colors.YELLOW)
    
    def run_all_checks(self) -> bool:
        """Run all setup checks"""
        log("🔍 Running setup checks...\n", color=Colors.BLUE)
        
        checks = [
            self.check_directory_structure(),
            self.check_required_files(),
            self.check_environment(),
            self.check_docker()
        ]
        
        self.generate_report()
        
        return all(checks)


class IntegrationTester:
    """Test LangGraph Flow integration"""
    
    def __init__(self):
        self.client = None
        self.test_results = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        log("Testing backend health...", color=Colors.BLUE)
        
        try:
            response = await self.client.get(f"{API_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                log(f"✅ Backend is {data.get('status', 'healthy')}", color=Colors.GREEN)
                
                # Check components
                components = data.get('components', {})
                for component, healthy in components.items():
                    if healthy:
                        log(f"  ✅ {component}: healthy", color=Colors.GREEN)
                    else:
                        log(f"  ❌ {component}: unhealthy", "ERROR", Colors.RED)
                
                return data.get('status') == 'healthy'
            else:
                log(f"❌ Backend returned {response.status_code}", "ERROR", Colors.RED)
                return False
        except Exception as e:
            log(f"❌ Backend connection failed: {e}", "ERROR", Colors.RED)
            return False
    
    async def test_airflow_connection(self) -> bool:
        """Test Airflow connection"""
        log("\nTesting Airflow connection...", color=Colors.BLUE)
        
        try:
            response = await self.client.get(
                f"{AIRFLOW_URL}/health",
                auth=("airflow", "airflow")
            )
            
            if response.status_code == 200:
                log("✅ Airflow is healthy", color=Colors.GREEN)
                
                # Check DAGs
                dags_response = await self.client.get(
                    f"{AIRFLOW_URL}/api/v1/dags",
                    auth=("airflow", "airflow")
                )
                
                if dags_response.status_code == 200:
                    dags = dags_response.json().get('dags', [])
                    log(f"  Found {len(dags)} DAGs", color=Colors.GREEN)
                
                return True
            else:
                log(f"❌ Airflow returned {response.status_code}", "ERROR", Colors.RED)
                return False
        except Exception as e:
            log(f"❌ Airflow connection failed: {e}", "ERROR", Colors.RED)
            return False
    
    async def test_langfuse_connection(self) -> bool:
        """Test LangFuse connection"""
        log("\nTesting LangFuse connection...", color=Colors.BLUE)
        
        try:
            response = await self.client.get(f"{LANGFUSE_HOST}/api/public/health")
            
            if response.status_code == 200:
                log("✅ LangFuse is healthy", color=Colors.GREEN)
                return True
            else:
                log(f"❌ LangFuse returned {response.status_code}", "ERROR", Colors.RED)
                return False
        except Exception as e:
            log(f"❌ LangFuse connection failed: {e}", "ERROR", Colors.RED)
            return False
    
    async def test_workflow_trigger(self) -> Optional[str]:
        """Test workflow triggering"""
        log("\nTesting workflow trigger...", color=Colors.BLUE)
        
        payload = {
            "dag_id": "visual_ai_workflow",
            "input_data": {
                "query": "Test workflow execution",
                "test": True
            },
            "user_id": "test_user"
        }
        
        try:
            response = await self.client.post(
                f"{API_URL}/api/v1/workflows/trigger",
                json=payload,
                headers={"Authorization": "Bearer test_token"}
            )
            
            if response.status_code == 200:
                data = response.json()
                dag_run_id = data.get('dag_run_id')
                log(f"✅ Workflow triggered: {dag_run_id}", color=Colors.GREEN)
                return dag_run_id
            else:
                log(f"❌ Trigger failed: {response.status_code}", "ERROR", Colors.RED)
                return None
        except Exception as e:
            log(f"❌ Trigger error: {e}", "ERROR", Colors.RED)
            return None
    
    async def run_all_tests(self):
        """Run all integration tests"""
        log("🚀 Running integration tests...\n", color=Colors.BLUE)
        
        # Basic health checks
        backend_ok = await self.test_backend_health()
        self.test_results.append(("Backend Health", backend_ok))
        
        airflow_ok = await self.test_airflow_connection()
        self.test_results.append(("Airflow Connection", airflow_ok))
        
        langfuse_ok = await self.test_langfuse_connection()
        self.test_results.append(("LangFuse Connection", langfuse_ok))
        
        # Only test workflow if services are healthy
        if backend_ok and airflow_ok:
            dag_run_id = await self.test_workflow_trigger()
            self.test_results.append(("Workflow Trigger", dag_run_id is not None))
        
        # Summary
        log("\n" + "="*60, color=Colors.BLUE)
        log("Test Summary", color=Colors.BLUE)
        log("="*60, color=Colors.BLUE)
        
        passed = sum(1 for _, ok in self.test_results if ok)
        total = len(self.test_results)
        
        for test_name, passed in self.test_results:
            if passed:
                log(f"  ✅ {test_name}", color=Colors.GREEN)
            else:
                log(f"  ❌ {test_name}", "ERROR", Colors.RED)
        
        log(f"\nTotal: {passed}/{total} tests passed", color=Colors.BLUE)
        
        if passed == total:
            log("🎉 All tests passed!", color=Colors.GREEN)
            return True
        else:
            log("⚠️  Some tests failed", "WARNING", Colors.YELLOW)
            return False


def test_langfuse_local():
    """Test local LangFuse integration"""
    if not LANGFUSE_AVAILABLE:
        log("❌ LangFuse package not installed", "ERROR", Colors.RED)
        log("  Run: pip install langfuse", color=Colors.YELLOW)
        return False
    
    log("🧪 Testing Local LangFuse Integration", color=Colors.BLUE)
    
    # Get configuration
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    
    if not public_key or not secret_key:
        log("❌ LangFuse keys not configured", "ERROR", Colors.RED)
        return False
    
    try:
        # Create client
        langfuse = Langfuse(
            host=LANGFUSE_HOST,
            public_key=public_key,
            secret_key=secret_key
        )
        
        # Create test trace
        trace = langfuse.trace(
            name="test-trace",
            metadata={"test": True}
        )
        
        # Create test generation
        trace.generation(
            name="test-generation",
            model="test-model",
            input="Hello, LangFuse!",
            output="Test successful!"
        )
        
        # Flush
        langfuse.flush()
        
        log("✅ LangFuse test successful!", color=Colors.GREEN)
        log(f"  View at: {LANGFUSE_HOST}", color=Colors.BLUE)
        return True
        
    except Exception as e:
        log(f"❌ LangFuse test failed: {e}", "ERROR", Colors.RED)
        return False


def test_ollama():
    """Test Ollama integration"""
    if not OLLAMA_AVAILABLE:
        log("❌ Ollama package not installed", "ERROR", Colors.RED)
        log("  Run: pip install langchain-ollama", color=Colors.YELLOW)
        return False
    
    log("🦙 Testing Ollama Integration", color=Colors.BLUE)
    
    try:
        from langchain_ollama import ChatOllama
        
        # Create model
        llm = ChatOllama(
            model="llama2",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        
        # Test generation
        response = llm.invoke("Say 'Ollama is working!'")
        log(f"✅ Ollama response: {response.content}", color=Colors.GREEN)
        
        return True
        
    except Exception as e:
        log(f"❌ Ollama test failed: {e}", "ERROR", Colors.RED)
        log("  Make sure Ollama is running and llama2 model is pulled", color=Colors.YELLOW)
        return False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LangGraph Flow Utilities")
    parser.add_argument('command', nargs='?', default='check',
                       choices=['check', 'test', 'test-langfuse', 'test-ollama'],
                       help='Command to run')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        checker = SetupChecker()
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)
    
    elif args.command == 'test':
        async with IntegrationTester() as tester:
            success = await tester.run_all_tests()
            sys.exit(0 if success else 1)
    
    elif args.command == 'test-langfuse':
        success = test_langfuse_local()
        sys.exit(0 if success else 1)
    
    elif args.command == 'test-ollama':
        success = test_ollama()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())