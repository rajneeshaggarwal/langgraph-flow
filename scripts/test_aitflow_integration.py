#!/usr/bin/env python3
"""
Test script for Airflow integration with LangGraph Flow
"""

import os
import sys
import time
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://localhost:8080")
TEST_TOKEN = os.getenv("TEST_TOKEN", "test_token")

class AirflowIntegrationTester:
    """Test suite for Airflow integration"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    async def test_health_check(self) -> bool:
        """Test health check endpoint"""
        self.log("Testing health check endpoint...")
        
        try:
            response = await self.client.get(f"{API_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health check passed: {data['status']}")
                
                # Check component health
                for component, healthy in data['components'].items():
                    status = "✅" if healthy else "❌"
                    self.log(f"  {status} {component}: {'healthy' if healthy else 'unhealthy'}")
                
                return data['status'] == 'healthy'
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {e}", "ERROR")
            return False
    
    async def test_workflow_trigger(self) -> Optional[str]:
        """Test workflow triggering"""
        self.log("Testing workflow trigger...")
        
        payload = {
            "dag_id": "visual_ai_workflow",
            "input_data": {
                "query": "Test workflow execution",
                "parameters": {
                    "test": True
                }
            },
            "user_id": "test_user"
        }
        
        try:
            response = await self.client.post(
                f"{API_URL}/api/v1/workflows/trigger",
                json=payload,
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                dag_run_id = data['dag_run_id']
                self.log(f"✅ Workflow triggered successfully: {dag_run_id}")
                return dag_run_id
            else:
                self.log(f"❌ Workflow trigger failed: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Workflow trigger error: {e}", "ERROR")
            return None
    
    async def test_workflow_status(self, dag_run_id: str) -> bool:
        """Test workflow status monitoring"""
        self.log(f"Testing workflow status for {dag_run_id}...")
        
        try:
            # Test non-streaming status endpoint
            response = await self.client.get(
                f"{API_URL}/api/v1/workflow-status/visual_ai_workflow/{dag_run_id}",
                headers={"Authorization": f"Bearer {TEST_TOKEN}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Workflow status retrieved: {data['state']}")
                self.log(f"  Progress: {data['progress']}%")
                self.log(f"  Tasks: {len(data['tasks'])}")
                return True
            else:
                self.log(f"❌ Status retrieval failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Status retrieval error: {e}", "ERROR")
            return False
    
    async def test_monitoring_endpoints(self) -> bool:
        """Test monitoring endpoints"""
        self.log("Testing monitoring endpoints...")
        
        endpoints = [
            "/api/v1/monitoring/workflow-metrics?time_range=24h",
            "/api/v1/monitoring/agent-performance?time_range=7d",
            "/api/v1/monitoring/error-distribution?time_range=24h",
            "/api/v1/monitoring/system-health"
        ]
        
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = await self.client.get(
                    f"{API_URL}{endpoint}",
                    headers={"Authorization": f"Bearer {TEST_TOKEN}"}
                )
                
                if response.status_code == 200:
                    self.log(f"  ✅ {endpoint}")
                else:
                    self.log(f"  ❌ {endpoint}: {response.status_code}", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"  ❌ {endpoint}: {e}", "ERROR")
                all_passed = False
        
        return all_passed
    
    async def test_airflow_connection(self) -> bool:
        """Test direct Airflow connection"""
        self.log("Testing Airflow connection...")
        
        try:
            response = await self.client.get(
                f"{AIRFLOW_URL}/health",
                auth=("airflow", "airflow")
            )
            
            if response.status_code == 200:
                self.log("✅ Airflow connection successful")
                
                # Check if DAGs are loaded
                dags_response = await self.client.get(
                    f"{AIRFLOW_URL}/api/v1/dags",
                    auth=("airflow", "airflow")
                )
                
                if dags_response.status_code == 200:
                    dags = dags_response.json()['dags']
                    visual_ai_dags = [d for d in dags if 'visual_ai' in d['dag_id']]
                    self.log(f"  Found {len(visual_ai_dags)} Visual AI DAGs")
                    for dag in visual_ai_dags:
                        self.log(f"    - {dag['dag_id']}: {'paused' if dag['is_paused'] else 'active'}")
                
                return True
            else:
                self.log(f"❌ Airflow connection failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Airflow connection error: {e}", "ERROR")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        self.log("🚀 Starting Airflow integration tests...")
        self.log("-" * 50)
        
        # Test 1: Health check
        health_passed = await self.test_health_check()
        self.test_results.append(("Health Check", health_passed))
        
        if not health_passed:
            self.log("⚠️  Health check failed, skipping remaining tests", "WARNING")
            return
        
        # Test 2: Airflow connection
        airflow_passed = await self.test_airflow_connection()
        self.test_results.append(("Airflow Connection", airflow_passed))
        
        # Test 3: Workflow trigger
        dag_run_id = await self.test_workflow_trigger()
        trigger_passed = dag_run_id is not None
        self.test_results.append(("Workflow Trigger", trigger_passed))
        
        if dag_run_id:
            # Wait a bit for workflow to start
            self.log("⏳ Waiting for workflow to start...")
            await asyncio.sleep(5)
            
            # Test 4: Workflow status
            status_passed = await self.test_workflow_status(dag_run_id)
            self.test_results.append(("Workflow Status", status_passed))
        
        # Test 5: Monitoring endpoints
        monitoring_passed = await self.test_monitoring_endpoints()
        self.test_results.append(("Monitoring Endpoints", monitoring_passed))
        
        # Summary
        self.log("-" * 50)
        self.log("📊 Test Summary:")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed in self.test_results if passed)
        
        for test_name, passed in self.test_results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"  {test_name}: {status}")
        
        self.log("-" * 50)
        self.log(f"Total: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 All tests passed! Airflow integration is working correctly.", "SUCCESS")
            return True
        else:
            self.log("⚠️  Some tests failed. Please check the logs above.", "WARNING")
            return False

async def main():
    """Main test runner"""
    async with AirflowIntegrationTester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    # Check if services are running
    print("🔍 Checking if services are running...")
    
    # You might want to add a check here to ensure Docker containers are up
    
    # Run tests
    asyncio.run(main())