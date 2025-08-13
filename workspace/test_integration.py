#!/usr/bin/env python3
"""Integration test to verify the ClinicLite application is working correctly"""

import requests
import json
import sys

def test_backend_api():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Backend API...")
    print("-" * 50)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Health check: {data['status']}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test dashboard
    try:
        response = requests.get(f"{base_url}/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Dashboard API: {len(data['upcoming_visits'])} upcoming, {len(data['missed_visits'])} missed, {len(data['low_stock_items'])} low stock")
    except Exception as e:
        print(f"✗ Dashboard API failed: {e}")
        return False
    
    # Test low stock items
    try:
        response = requests.get(f"{base_url}/api/stock/low-items")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Low stock API: {len(data)} items")
    except Exception as e:
        print(f"✗ Low stock API failed: {e}")
        return False
    
    # Test stats
    try:
        response = requests.get(f"{base_url}/api/stats")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Stats API: {data['clinics']} clinics, {data['patients']} patients")
    except Exception as e:
        print(f"✗ Stats API failed: {e}")
        return False
    
    return True

def test_frontend():
    """Test frontend is accessible"""
    base_url = "http://localhost:3001"
    
    print("\nTesting Frontend...")
    print("-" * 50)
    
    try:
        response = requests.get(base_url)
        assert response.status_code == 200
        assert "ClinicLite Botswana" in response.text
        print(f"✓ Frontend accessible at {base_url}")
    except Exception as e:
        print(f"✗ Frontend failed: {e}")
        return False
    
    # Test static assets
    for asset in ["/app.js", "/styles.css"]:
        try:
            response = requests.get(f"{base_url}{asset}")
            assert response.status_code == 200
            print(f"✓ Asset {asset} loaded")
        except Exception as e:
            print(f"✗ Asset {asset} failed: {e}")
            return False
    
    return True

def test_cors():
    """Test CORS is properly configured"""
    print("\nTesting CORS Configuration...")
    print("-" * 50)
    
    headers = {
        'Origin': 'http://localhost:3001',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options("http://localhost:8000/api/dashboard", headers=headers)
        cors_headers = response.headers.get('access-control-allow-origin', '')
        
        if '*' in cors_headers or 'http://localhost:3001' in cors_headers:
            print(f"✓ CORS configured: {cors_headers}")
            return True
        else:
            print(f"✗ CORS not properly configured")
            return False
    except Exception as e:
        print(f"✗ CORS test failed: {e}")
        return False

def main():
    print("=" * 50)
    print("ClinicLite Integration Test")
    print("=" * 50)
    
    backend_ok = test_backend_api()
    frontend_ok = test_frontend()
    cors_ok = test_cors()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    if backend_ok and frontend_ok and cors_ok:
        print("✓ All tests passed! Application is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())