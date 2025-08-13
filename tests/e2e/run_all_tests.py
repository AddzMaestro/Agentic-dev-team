#!/usr/bin/env python3
"""
Comprehensive Playwright Test Runner for ClinicLite Botswana
Executes all test suites and generates detailed reports
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test configuration
TEST_CONFIG = {
    "BASE_URL": "http://localhost:3001",
    "API_URL": "http://localhost:8000",
    "HEADLESS": True,
    "TIMEOUT": 30000,
    "SLOW_MO": 100,  # Milliseconds between actions for human-like interaction
    "SCREENSHOTS": True,
    "VIDEO": False,
    "TRACE": False
}

# Test suites to run
TEST_SUITES = [
    "test_csv_upload_comprehensive.py",
    "test_dashboard_functionality.py", 
    "test_sms_reminder_functionality.py",
    "test_stock_management.py",
    "test_offline_functionality.py",
    "test_error_handling.py"
]

def ensure_directories():
    """Ensure all required directories exist"""
    dirs = [
        "/Users/addzmaestro/coding projects/Claude system/workspace/reports",
        "/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots",
        "/Users/addzmaestro/coding projects/Claude system/workspace/reports/test_results",
        "/Users/addzmaestro/coding projects/Claude system/workspace/reports/coverage"
    ]
    
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Created report directories")

def check_services():
    """Check if backend and frontend services are running"""
    import requests
    
    services_ok = True
    
    # Check backend
    try:
        response = requests.get(TEST_CONFIG["API_URL"])
        if response.status_code == 200:
            print(f"✓ Backend is running at {TEST_CONFIG['API_URL']}")
        else:
            print(f"✗ Backend returned status {response.status_code}")
            services_ok = False
    except Exception as e:
        print(f"✗ Backend is not accessible: {e}")
        services_ok = False
    
    # Check frontend
    try:
        response = requests.get(TEST_CONFIG["BASE_URL"])
        if response.status_code == 200:
            print(f"✓ Frontend is running at {TEST_CONFIG['BASE_URL']}")
        else:
            print(f"✗ Frontend returned status {response.status_code}")
            services_ok = False
    except Exception as e:
        print(f"✗ Frontend is not accessible: {e}")
        services_ok = False
    
    return services_ok

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "pytest",
        "pytest-playwright",
        "pytest-asyncio",
        "pytest-html",
        "pytest-json-report",
        "aiohttp"
    ]
    
    print("Installing test dependencies...")
    for package in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", package])
    
    print("✓ Test dependencies installed")

def run_playwright_install():
    """Install Playwright browsers"""
    print("Installing Playwright browsers...")
    result = subprocess.run(
        ["npx", "playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Playwright browsers installed")
    else:
        print(f"⚠ Playwright installation: {result.stderr}")

def generate_test_report(results):
    """Generate HTML test report"""
    report_path = "/Users/addzmaestro/coding projects/Claude system/workspace/reports/test_report.html"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ClinicLite Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2e7d32; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .test-suite {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .passed {{ color: #2e7d32; font-weight: bold; }}
        .failed {{ color: #d32f2f; font-weight: bold; }}
        .skipped {{ color: #ff9800; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; }}
        .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; background: white; border-radius: 5px; flex: 1; margin: 0 10px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2e7d32; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ClinicLite Botswana - Playwright Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Test Execution Summary</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{results.get('total', 0)}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric">
                <div class="metric-value passed">{results.get('passed', 0)}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value failed">{results.get('failed', 0)}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value skipped">{results.get('skipped', 0)}</div>
                <div class="metric-label">Skipped</div>
            </div>
        </div>
        
        <h3>Pass Rate: {results.get('pass_rate', 0):.1f}%</h3>
        <p>Duration: {results.get('duration', 0):.2f} seconds</p>
    </div>
    
    <div class="test-suite">
        <h2>Test Suites</h2>
        <table>
            <thead>
                <tr>
                    <th>Test Suite</th>
                    <th>Tests</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Duration (s)</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for suite in results.get('suites', []):
        html_content += f"""
                <tr>
                    <td>{suite['name']}</td>
                    <td>{suite['total']}</td>
                    <td class="passed">{suite['passed']}</td>
                    <td class="failed">{suite['failed']}</td>
                    <td>{suite['duration']:.2f}</td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="test-suite">
        <h2>Test Coverage Areas</h2>
        <ul>
            <li>✓ CSV Upload (4 entity types: clinics, patients, appointments, stock)</li>
            <li>✓ Dashboard Display (upcoming visits, missed visits, low stock)</li>
            <li>✓ SMS Reminders (language toggle EN/TSW, preview, queue)</li>
            <li>✓ Stock Management (low stock detection, reorder draft)</li>
            <li>✓ Offline Functionality (connection status, local storage, sync)</li>
            <li>✓ Error Handling (validation, malformed data, edge cases)</li>
        </ul>
    </div>
    
    <div class="test-suite">
        <h2>Screenshots</h2>
        <p>Test screenshots are available in: workspace/reports/screenshots/</p>
    </div>
</body>
</html>
"""
    
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    print(f"✓ HTML report generated: {report_path}")
    return report_path

async def run_tests():
    """Run all Playwright tests"""
    print("\n" + "="*60)
    print("CLINCLITE BOTSWANA - COMPREHENSIVE PLAYWRIGHT TESTS")
    print("="*60 + "\n")
    
    # Setup
    ensure_directories()
    install_dependencies()
    run_playwright_install()
    
    # Check services
    if not check_services():
        print("\n⚠ Warning: Services may not be running properly")
        print("Please ensure backend (port 8000) and frontend (port 3001) are running")
        return
    
    print("\n" + "-"*40)
    print("Running Test Suites...")
    print("-"*40 + "\n")
    
    # Run tests
    test_dir = Path(__file__).parent
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'suites': [],
        'start_time': datetime.now()
    }
    
    for test_file in TEST_SUITES:
        test_path = test_dir / test_file
        if not test_path.exists():
            print(f"⚠ Test file not found: {test_file}")
            continue
        
        print(f"Running {test_file}...")
        
        # Run pytest with playwright
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            f"--json-report-file=/Users/addzmaestro/coding projects/Claude system/workspace/reports/test_results/{test_file}.json",
            "--headed" if not TEST_CONFIG["HEADLESS"] else "",
            "-m", "e2e"
        ]
        
        # Remove empty strings from command
        cmd = [c for c in cmd if c]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        suite_result = {
            'name': test_file.replace('.py', ''),
            'total': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0
        }
        
        # Simple parsing from pytest output
        if "passed" in result.stdout:
            import re
            match = re.search(r'(\d+) passed', result.stdout)
            if match:
                suite_result['passed'] = int(match.group(1))
        
        if "failed" in result.stdout:
            import re
            match = re.search(r'(\d+) failed', result.stdout)
            if match:
                suite_result['failed'] = int(match.group(1))
        
        suite_result['total'] = suite_result['passed'] + suite_result['failed']
        results['suites'].append(suite_result)
        
        results['total'] += suite_result['total']
        results['passed'] += suite_result['passed']
        results['failed'] += suite_result['failed']
        
        # Print suite summary
        status = "✓" if suite_result['failed'] == 0 else "✗"
        print(f"{status} {test_file}: {suite_result['passed']}/{suite_result['total']} passed")
    
    # Calculate final metrics
    end_time = datetime.now()
    results['duration'] = (end_time - results['start_time']).total_seconds()
    results['pass_rate'] = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    
    # Generate reports
    print("\n" + "-"*40)
    print("Generating Reports...")
    print("-"*40 + "\n")
    
    report_path = generate_test_report(results)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST EXECUTION COMPLETE")
    print("="*60 + "\n")
    
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ({results['pass_rate']:.1f}%)")
    print(f"Failed: {results['failed']}")
    print(f"Duration: {results['duration']:.2f} seconds")
    
    print(f"\n📊 Full report: {report_path}")
    print(f"📸 Screenshots: /Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/")
    
    # Return exit code based on failures
    return 0 if results['failed'] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)