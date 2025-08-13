"""
Simple synchronous tests for ClinicLite validation
Tests basic functionality without async complexity
"""

import requests
import json
import time
import tempfile
import csv
import os

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

class TestBasicFunctionality:
    """Basic functionality tests"""
    
    def test_backend_health_check(self):
        """Test that backend server is running"""
        response = requests.get(f"{API_URL}/")
        assert response.status_code == 200
        print("✅ Backend server is healthy")
    
    def test_frontend_accessible(self):
        """Test that frontend is accessible"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        assert "ClinicLite" in response.text
        print("✅ Frontend is accessible")
    
    def test_api_dashboard_endpoint(self):
        """Test dashboard API endpoint"""
        response = requests.get(f"{API_URL}/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "upcoming_visits" in data
        assert "missed_visits" in data
        print(f"✅ Dashboard API working - {len(data.get('upcoming_visits', []))} upcoming visits")
    
    def test_api_stats_endpoint(self):
        """Test stats API endpoint"""
        response = requests.get(f"{API_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_patients" in data
        assert "total_clinics" in data
        print(f"✅ Stats API working - {data.get('total_patients', 0)} patients")
    
    def test_api_low_stock_endpoint(self):
        """Test low stock API endpoint"""
        response = requests.get(f"{API_URL}/api/stock/low-items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Low stock API working - {len(data)} items low")
    
    def test_csv_upload_clinics(self):
        """Test CSV upload for clinics"""
        # Create test CSV
        csv_content = "clinic_id,name,district,phone,email\nCL001,Test Clinic,Central,+267-71234567,test@clinic.bw"
        
        files = {
            'file': ('clinics.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("success") == True
        print(f"✅ Clinic CSV upload successful - {result.get('records_processed', 0)} records")
    
    def test_csv_upload_patients(self):
        """Test CSV upload for patients"""
        csv_content = "patient_id,first_name,last_name,dob,phone_e164,preferred_lang\nP001,John,Doe,1990-01-01,+26771234567,EN"
        
        files = {
            'file': ('patients.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=patients",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("success") == True
        print(f"✅ Patient CSV upload successful - {result.get('records_processed', 0)} records")
    
    def test_csv_upload_appointments(self):
        """Test CSV upload for appointments"""
        csv_content = "appointment_id,patient_id,clinic_id,next_visit_date,visit_type\nA001,P001,CL001,2025-08-15,routine"
        
        files = {
            'file': ('appointments.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=appointments",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("success") == True
        print(f"✅ Appointment CSV upload successful - {result.get('records_processed', 0)} records")
    
    def test_csv_upload_stock(self):
        """Test CSV upload for stock"""
        csv_content = "stock_id,clinic_id,item_name,on_hand_qty,reorder_level,unit\nS001,CL001,Paracetamol,50,100,tablets"
        
        files = {
            'file': ('stock.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=stock",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("success") == True
        print(f"✅ Stock CSV upload successful - {result.get('records_processed', 0)} records")
    
    def test_sms_send_endpoint(self):
        """Test SMS send endpoint"""
        payload = {
            "patient_id": "P001",
            "appointment_date": "2025-08-15",
            "language": "EN"
        }
        
        response = requests.post(
            f"{API_URL}/api/sms/send",
            json=payload
        )
        
        # Should either succeed or return appropriate error
        assert response.status_code in [200, 404]  # 404 if patient not found
        print(f"✅ SMS endpoint responding - status {response.status_code}")
    
    def test_sms_queue_endpoint(self):
        """Test SMS queue endpoint"""
        response = requests.get(f"{API_URL}/api/sms/queue")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ SMS queue endpoint working - {len(data)} messages in queue")
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = requests.options(
            f"{API_URL}/api/dashboard",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        print(f"✅ CORS configured correctly")


class TestEdgeCases:
    """Edge case tests"""
    
    def test_empty_csv_upload(self):
        """Test uploading empty CSV"""
        csv_content = "clinic_id,name,district,phone,email"  # Headers only
        
        files = {
            'file': ('empty.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        print(f"✅ Empty CSV handled - {result.get('records_processed', 0)} records")
    
    def test_invalid_file_type(self):
        """Test invalid file type parameter"""
        files = {
            'file': ('test.csv', 'test,data', 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=invalid",
            files=files
        )
        
        assert response.status_code in [400, 422]
        print(f"✅ Invalid file type rejected - status {response.status_code}")
    
    def test_missing_file_upload(self):
        """Test upload without file"""
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics"
        )
        
        assert response.status_code in [400, 422]
        print(f"✅ Missing file rejected - status {response.status_code}")
    
    def test_malformed_csv(self):
        """Test malformed CSV data"""
        csv_content = "this is not,proper csv\ndata at all"
        
        files = {
            'file': ('malformed.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics",
            files=files
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
        print(f"✅ Malformed CSV handled - status {response.status_code}")
    
    def test_sql_injection_attempt(self):
        """Test SQL injection prevention"""
        csv_content = "clinic_id,name,district,phone,email\nCL001,'; DROP TABLE clinics;--,Central,+267-71234567,test@test.com"
        
        files = {
            'file': ('injection.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics",
            files=files
        )
        
        # Should process safely
        assert response.status_code == 200
        
        # Verify tables still exist
        check = requests.get(f"{API_URL}/api/dashboard")
        assert check.status_code == 200
        print(f"✅ SQL injection prevented - database intact")
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        csv_content = 'clinic_id,name,district,phone,email\nCL001,<script>alert("XSS")</script>,Central,+267-71234567,test@test.com'
        
        files = {
            'file': ('xss.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics",
            files=files
        )
        
        assert response.status_code == 200
        
        # Check dashboard doesn't contain unescaped script
        dashboard = requests.get(f"{API_URL}/api/dashboard")
        assert '<script>' not in dashboard.text or '&lt;script&gt;' in dashboard.text
        print(f"✅ XSS prevention working")
    
    def test_duplicate_ids(self):
        """Test handling of duplicate IDs"""
        csv_content = "patient_id,first_name,last_name,dob,phone_e164,preferred_lang\nP999,John,Doe,1990-01-01,+26771234567,EN\nP999,Jane,Smith,1985-01-01,+26771234568,TSW"
        
        files = {
            'file': ('duplicates.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=patients",
            files=files
        )
        
        # Should handle duplicates gracefully
        assert response.status_code == 200
        print(f"✅ Duplicate IDs handled")
    
    def test_concurrent_requests(self):
        """Test concurrent API requests"""
        import concurrent.futures
        
        def make_request():
            return requests.get(f"{API_URL}/api/dashboard")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
        print(f"✅ Handled {len(results)} concurrent requests")
    
    def test_large_csv_upload(self):
        """Test uploading large CSV"""
        # Create CSV with 500 rows
        csv_lines = ["patient_id,first_name,last_name,dob,phone_e164,preferred_lang"]
        for i in range(500):
            csv_lines.append(f"PL{i:04d},First{i},Last{i},1990-01-01,+2677123{i:04d},EN")
        
        csv_content = "\n".join(csv_lines)
        
        files = {
            'file': ('large.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=patients",
            files=files,
            timeout=10
        )
        
        assert response.status_code == 200
        result = response.json()
        print(f"✅ Large CSV processed - {result.get('records_processed', 0)} records")
    
    def test_special_characters(self):
        """Test handling of special characters"""
        csv_content = 'clinic_id,name,district,phone,email\nCL001,"Test & Clinic, Ltd.",North-East,+267-71234567,test@clinic.bw'
        
        files = {
            'file': ('special.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{API_URL}/api/upload?file_type=clinics",
            files=files
        )
        
        assert response.status_code == 200
        print(f"✅ Special characters handled correctly")


class TestPerformance:
    """Performance tests"""
    
    def test_dashboard_response_time(self):
        """Test dashboard response time"""
        start = time.time()
        response = requests.get(f"{API_URL}/api/dashboard")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Should respond within 2 seconds
        print(f"✅ Dashboard responded in {duration:.3f}s")
    
    def test_api_response_times(self):
        """Test various API response times"""
        endpoints = [
            "/api/dashboard",
            "/api/stats",
            "/api/stock/low-items",
            "/api/sms/queue"
        ]
        
        for endpoint in endpoints:
            start = time.time()
            response = requests.get(f"{API_URL}{endpoint}")
            duration = time.time() - start
            
            assert response.status_code == 200
            assert duration < 1.0  # Each should respond within 1 second
            print(f"✅ {endpoint} responded in {duration:.3f}s")
    
    def test_upload_processing_time(self):
        """Test CSV upload processing time"""
        # Create CSV with 100 rows
        csv_lines = ["patient_id,first_name,last_name,dob,phone_e164,preferred_lang"]
        for i in range(100):
            csv_lines.append(f"PT{i:04d},First{i},Last{i},1990-01-01,+2677123{i:04d},EN")
        
        csv_content = "\n".join(csv_lines)
        
        files = {
            'file': ('perf.csv', csv_content, 'text/csv')
        }
        
        start = time.time()
        response = requests.post(
            f"{API_URL}/api/upload?file_type=patients",
            files=files
        )
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should process 100 records in under 1 second
        print(f"✅ Processed 100 records in {duration:.3f}s")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])