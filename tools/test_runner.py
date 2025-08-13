#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner for Autonomous Workflow
Runs Playwright tests and outputs standardized JSON results
"""
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# ULTRA-THINK: Pre-mortem - What could go wrong?
# - Tests might not exist yet
# - Playwright might not be installed
# - Backend/Frontend might not be running
# - Results directory might not exist

def ensure_services_running():
    """Check if backend and frontend are accessible"""
    import requests
    import time
    
    checks = {
        "backend": "http://localhost:8000/api/",
        "frontend": "http://localhost:3001/"
    }
    
    for service, url in checks.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                print(f"✓ {service.capitalize()} is running at {url}")
            else:
                print(f"⚠ {service.capitalize()} returned {response.status_code}")
        except Exception as e:
            print(f"✗ {service.capitalize()} not accessible: {e}")
            return False
    return True

def run_playwright_tests():
    """Execute Playwright tests and capture results"""
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    test_dir = project_dir / "tests" / "e2e"
    test_file = test_dir / "clinicLiteAuto.spec.js"
    
    # Check if test file exists
    if not test_file.exists():
        print(f"⚠ Test file not found: {test_file}")
        return {
            "passed": False,
            "total": 0,
            "failed": 0,
            "message": f"Test file {test_file} does not exist",
            "timestamp": datetime.now().isoformat()
        }
    
    # Run Playwright tests
    try:
        print(f"Running tests from {test_file}...")
        cmd = [
            "npx", "playwright", "test",
            str(test_file),
            "--reporter=json"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(project_dir)
        )
        
        # Parse results from stdout (JSON reporter outputs to stdout)
        if result.stdout:
            try:
                report = json.loads(result.stdout)
                # Playwright JSON reporter format
                passed = report.get("stats", {}).get("unexpected", 0) == 0
                total = report.get("stats", {}).get("total", 0)
                failed = report.get("stats", {}).get("unexpected", 0)
                
                return {
                    "passed": passed,
                    "total": total,
                    "failed": failed,
                    "passed_count": total - failed,
                    "details": report,
                    "timestamp": datetime.now().isoformat()
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: parse from stdout
        stdout = result.stdout
        passed = result.returncode == 0
        
        # Try to extract test counts from output
        total = stdout.count("✓") + stdout.count("✘")
        failed = stdout.count("✘")
        
        return {
            "passed": passed,
            "total": total,
            "failed": failed,
            "passed_count": total - failed,
            "stdout": stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timestamp": datetime.now().isoformat()
        }
            
    except Exception as e:
        print(f"✗ Test execution failed: {e}")
        return {
            "passed": False,
            "total": 0,
            "failed": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def write_results(results):
    """Write test results to expected location"""
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    reports_dir = project_dir / "workspace" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    result_file = reports_dir / "last_test_result.json"
    
    with open(result_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results written to {result_file}")
    print(f"   Passed: {results['passed']}")
    print(f"   Total tests: {results.get('total', 0)}")
    print(f"   Failed: {results.get('failed', 0)}")
    
    return result_file

def main():
    """Main test runner entry point"""
    print("=" * 60)
    print("🚀 ClinicLite Autonomous Test Runner")
    print("=" * 60)
    
    # Step 1: Check services
    print("\n1. Checking services...")
    if not ensure_services_running():
        print("⚠ Warning: Services may not be running properly")
    
    # Step 2: Run tests
    print("\n2. Running Playwright tests...")
    results = run_playwright_tests()
    
    # Step 3: Write results
    print("\n3. Writing results...")
    result_file = write_results(results)
    
    # Step 4: Exit with appropriate code
    if results["passed"]:
        print("\n✅ All tests passed! Ready for production.")
        sys.exit(0)
    else:
        print(f"\n❌ Tests failed. {results.get('failed', 'Unknown')} test(s) need fixing.")
        sys.exit(1)

if __name__ == "__main__":
    main()