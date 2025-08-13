#!/usr/bin/env python3
"""
Comprehensive Test Runner for ClinicLite Botswana
Executes all test suites and generates detailed reports
"""

import asyncio
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

# Test configuration
BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"
REPORTS_DIR = "/Users/addzmaestro/coding projects/Claude system/workspace/reports"
SCREENSHOTS_DIR = f"{REPORTS_DIR}/screenshots"

# Test suites to run
TEST_SUITES = [
    {
        'name': 'Edge Cases Comprehensive',
        'file': 'test_edge_cases_comprehensive.py',
        'marks': ['edge'],
        'critical': True
    },
    {
        'name': 'CSV Upload Comprehensive',
        'file': 'test_csv_upload_comprehensive.py',
        'marks': ['e2e'],
        'critical': True
    },
    {
        'name': 'Dashboard Functionality',
        'file': 'test_dashboard_functionality.py',
        'marks': ['e2e'],
        'critical': True
    },
    {
        'name': 'SMS Reminder Functionality',
        'file': 'test_sms_reminder_functionality.py',
        'marks': ['e2e'],
        'critical': True
    },
    {
        'name': 'Stock Management',
        'file': 'test_stock_management.py',
        'marks': ['e2e'],
        'critical': True
    },
    {
        'name': 'Error Handling',
        'file': 'test_error_handling.py',
        'marks': ['e2e'],
        'critical': True
    },
    {
        'name': 'Offline Functionality',
        'file': 'test_offline_functionality.py',
        'marks': ['e2e'],
        'critical': False
    },
    {
        'name': 'User Journey',
        'file': 'test_user_journey.py',
        'marks': ['e2e'],
        'critical': True
    }
]

class TestRunner:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.critical_failures = []
        
        # Ensure directories exist
        Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
        Path(SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
    
    def check_servers(self):
        """Check if backend and frontend servers are running"""
        import requests
        
        servers_ok = True
        
        # Check backend
        try:
            response = requests.get(f"{API_URL}/", timeout=5)
            print(f"✅ Backend server is running at {API_URL}")
        except:
            print(f"❌ Backend server is not accessible at {API_URL}")
            servers_ok = False
        
        # Check frontend
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            print(f"✅ Frontend server is running at {BASE_URL}")
        except:
            print(f"❌ Frontend server is not accessible at {BASE_URL}")
            servers_ok = False
        
        return servers_ok
    
    def run_test_suite(self, suite):
        """Run a single test suite"""
        print(f"\n{'='*60}")
        print(f"Running: {suite['name']}")
        print(f"File: {suite['file']}")
        print(f"Marks: {', '.join(suite['marks'])}")
        print(f"Critical: {suite['critical']}")
        print(f"{'='*60}")
        
        # Construct pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            suite['file'],
            "-v",
            "--tb=short",
            f"--junit-xml={REPORTS_DIR}/{suite['file']}.xml",
            "--capture=no"
        ]
        
        # Add marks
        for mark in suite['marks']:
            cmd.extend(["-m", mark])
        
        # Run the tests
        start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        duration = time.time() - start
        
        # Parse results
        suite_result = {
            'name': suite['name'],
            'file': suite['file'],
            'critical': suite['critical'],
            'return_code': result.returncode,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
        
        # Parse XML results if available
        xml_file = f"{REPORTS_DIR}/{suite['file']}.xml"
        if os.path.exists(xml_file):
            suite_result.update(self.parse_junit_xml(xml_file))
        
        self.results.append(suite_result)
        
        # Print summary
        if suite_result['passed']:
            print(f"✅ {suite['name']} PASSED in {duration:.2f}s")
        else:
            print(f"❌ {suite['name']} FAILED in {duration:.2f}s")
            if suite['critical']:
                self.critical_failures.append(suite['name'])
        
        return suite_result
    
    def parse_junit_xml(self, xml_file):
        """Parse JUnit XML results"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            testsuite = root.find('.//testsuite')
            if testsuite is not None:
                return {
                    'tests': int(testsuite.get('tests', 0)),
                    'failures': int(testsuite.get('failures', 0)),
                    'errors': int(testsuite.get('errors', 0)),
                    'skipped': int(testsuite.get('skipped', 0)),
                    'time': float(testsuite.get('time', 0))
                }
        except Exception as e:
            print(f"Error parsing XML: {e}")
        
        return {}
    
    def generate_html_report(self):
        """Generate comprehensive HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ClinicLite Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .suite {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .passed {{ border-left: 5px solid #27ae60; }}
        .failed {{ border-left: 5px solid #e74c3c; }}
        .critical {{ background: #ffe5e5; }}
        .stats {{ display: flex; justify-content: space-around; }}
        .stat-box {{ text-align: center; padding: 10px; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .progress-bar {{ width: 100%; height: 30px; background: #ecf0f1; border-radius: 15px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #27ae60, #2ecc71); transition: width 0.3s; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
        .error-log {{ background: #2c3e50; color: #fff; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 ClinicLite Botswana - Comprehensive Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Duration: {(self.end_time - self.start_time):.2f} seconds</p>
    </div>
    
    <div class="summary">
        <h2>Test Summary</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{self.total_tests}</div>
                <div>Total Tests</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #27ae60;">{self.passed_tests}</div>
                <div>Passed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #e74c3c;">{self.failed_tests}</div>
                <div>Failed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #f39c12;">{self.skipped_tests}</div>
                <div>Skipped</div>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {(self.passed_tests / max(self.total_tests, 1)) * 100}%;"></div>
            </div>
            <p style="text-align: center; margin-top: 10px;">
                Pass Rate: {(self.passed_tests / max(self.total_tests, 1)) * 100:.1f}%
            </p>
        </div>
    </div>
    
    <div class="summary">
        <h2>Test Suites</h2>
        <table>
            <tr>
                <th>Suite Name</th>
                <th>Status</th>
                <th>Tests</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Duration</th>
                <th>Critical</th>
            </tr>
"""
        
        for result in self.results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            critical = "Yes" if result['critical'] else "No"
            tests = result.get('tests', 0)
            failures = result.get('failures', 0)
            passed = tests - failures
            
            html_content += f"""
            <tr class="{'failed' if not result['passed'] else ''}">
                <td>{result['name']}</td>
                <td>{status}</td>
                <td>{tests}</td>
                <td>{passed}</td>
                <td>{failures}</td>
                <td>{result['duration']:.2f}s</td>
                <td>{critical}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
"""
        
        # Add critical failures section if any
        if self.critical_failures:
            html_content += f"""
    <div class="summary critical">
        <h2>⚠️ Critical Failures</h2>
        <p>The following critical test suites failed:</p>
        <ul>
"""
            for failure in self.critical_failures:
                html_content += f"            <li>{failure}</li>\n"
            
            html_content += """
        </ul>
    </div>
"""
        
        # Add detailed results for failed tests
        failed_suites = [r for r in self.results if not r['passed']]
        if failed_suites:
            html_content += """
    <div class="summary">
        <h2>Failed Test Details</h2>
"""
            for suite in failed_suites:
                html_content += f"""
        <div class="suite failed">
            <h3>{suite['name']}</h3>
            <div class="error-log">
                <pre>{suite.get('stderr', 'No error output available')}</pre>
            </div>
        </div>
"""
        
        html_content += """
    <div class="summary">
        <h2>Test Categories</h2>
        <ul>
            <li><strong>Edge Cases:</strong> Tests for boundary conditions, invalid inputs, and unusual scenarios</li>
            <li><strong>Security:</strong> SQL injection, XSS, CSRF, and other security vulnerabilities</li>
            <li><strong>Performance:</strong> Load testing, concurrent users, and response time validation</li>
            <li><strong>Frontend:</strong> UI interactions, browser compatibility, and user experience</li>
            <li><strong>API:</strong> Endpoint validation, error handling, and data integrity</li>
        </ul>
    </div>
    
    <div class="summary">
        <h2>Screenshots</h2>
        <p>Test screenshots are available in: {SCREENSHOTS_DIR}</p>
    </div>
</body>
</html>
"""
        
        # Save HTML report
        report_path = f"{REPORTS_DIR}/comprehensive_test_report.html"
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        print(f"\n📊 HTML report generated: {report_path}")
        
        return report_path
    
    def generate_summary(self):
        """Generate and print test summary"""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        
        # Calculate totals
        for result in self.results:
            if 'tests' in result:
                self.total_tests += result['tests']
                self.passed_tests += (result['tests'] - result.get('failures', 0) - result.get('errors', 0))
                self.failed_tests += result.get('failures', 0) + result.get('errors', 0)
                self.skipped_tests += result.get('skipped', 0)
        
        print(f"Total Test Suites: {len(self.results)}")
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Skipped: {self.skipped_tests}")
        print(f"Pass Rate: {(self.passed_tests / max(self.total_tests, 1)) * 100:.1f}%")
        print(f"Total Duration: {(self.end_time - self.start_time):.2f} seconds")
        
        if self.critical_failures:
            print("\n⚠️  CRITICAL FAILURES DETECTED:")
            for failure in self.critical_failures:
                print(f"  - {failure}")
            print("\nThese critical failures must be fixed for zero-error delivery!")
        else:
            print("\n✅ All critical tests passed!")
        
        # Determine overall status
        if self.failed_tests == 0:
            print("\n🎉 SUCCESS: All tests passed! Ready for delivery.")
            return 0
        elif len(self.critical_failures) == 0:
            print("\n⚠️  WARNING: Some non-critical tests failed.")
            return 1
        else:
            print("\n❌ FAILURE: Critical tests failed. Fix required before delivery.")
            return 2
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("\n🚀 Starting Comprehensive Test Suite for ClinicLite Botswana")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check servers
        if not self.check_servers():
            print("\n❌ ERROR: Servers are not running. Please start both backend and frontend servers.")
            return 3
        
        self.start_time = time.time()
        
        # Run each test suite
        for suite in TEST_SUITES:
            self.run_test_suite(suite)
            # Small delay between suites
            await asyncio.sleep(1)
        
        self.end_time = time.time()
        
        # Generate reports
        self.generate_html_report()
        status = self.generate_summary()
        
        return status


async def main():
    """Main entry point"""
    runner = TestRunner()
    status = await runner.run_all_tests()
    
    # Write status to file for CI/CD integration
    with open(f"{REPORTS_DIR}/test_status.json", 'w') as f:
        json.dump({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'total_tests': runner.total_tests,
            'passed': runner.passed_tests,
            'failed': runner.failed_tests,
            'critical_failures': runner.critical_failures
        }, f, indent=2)
    
    sys.exit(status)


if __name__ == "__main__":
    asyncio.run(main())