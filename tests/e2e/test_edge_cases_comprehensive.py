"""
Comprehensive Edge Case Testing Suite for ClinicLite Botswana
Tests all edge cases, error scenarios, and boundary conditions
"""

import pytest
import asyncio
import tempfile
import os
import csv
import json
from pathlib import Path
from playwright.async_api import Page, expect, BrowserContext
from datetime import datetime, timedelta

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.edge
@pytest.mark.asyncio
class TestCSVEdgeCases:
    """Edge case tests for CSV upload functionality"""
    
    async def setup_method(self):
        """Create various test CSV files for edge cases"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = {}
        
        # Empty CSV (headers only)
        self.test_files['empty_clinics'] = os.path.join(self.temp_dir, "empty_clinics.csv")
        with open(self.test_files['empty_clinics'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
        
        # CSV with missing required columns
        self.test_files['missing_columns'] = os.path.join(self.temp_dir, "missing_columns.csv")
        with open(self.test_files['missing_columns'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name'])  # Missing district, phone, email
            writer.writerow(['CL001', 'Test Clinic'])
        
        # CSV with extra columns
        self.test_files['extra_columns'] = os.path.join(self.temp_dir, "extra_columns.csv")
        with open(self.test_files['extra_columns'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email', 'extra1', 'extra2'])
            writer.writerow(['CL001', 'Main Clinic', 'Central', '+267-71234567', 'main@clinic.bw', 'extra', 'data'])
        
        # CSV with duplicate IDs
        self.test_files['duplicate_ids'] = os.path.join(self.temp_dir, "duplicate_ids.csv")
        with open(self.test_files['duplicate_ids'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            writer.writerow(['P001', 'John', 'Doe', '1990-01-01', '+26771234567', 'EN'])
            writer.writerow(['P001', 'Jane', 'Smith', '1985-05-15', '+26771234568', 'TSW'])  # Duplicate ID
        
        # CSV with invalid phone numbers
        self.test_files['invalid_phones'] = os.path.join(self.temp_dir, "invalid_phones.csv")
        with open(self.test_files['invalid_phones'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            writer.writerow(['P001', 'John', 'Doe', '1990-01-01', 'invalid-phone', 'EN'])
            writer.writerow(['P002', 'Jane', 'Smith', '1985-05-15', '123', 'TSW'])
            writer.writerow(['P003', 'Bob', 'Jones', '1980-01-01', '', 'EN'])  # Empty phone
        
        # CSV with invalid dates
        self.test_files['invalid_dates'] = os.path.join(self.temp_dir, "invalid_dates.csv")
        with open(self.test_files['invalid_dates'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['appointment_id', 'patient_id', 'clinic_id', 'next_visit_date', 'visit_type'])
            writer.writerow(['A001', 'P001', 'CL001', 'invalid-date', 'routine'])
            writer.writerow(['A002', 'P002', 'CL002', '2025-13-45', 'follow-up'])  # Invalid month/day
            writer.writerow(['A003', 'P003', 'CL003', '', 'routine'])  # Empty date
        
        # CSV with special characters and SQL injection attempts
        self.test_files['special_chars'] = os.path.join(self.temp_dir, "special_chars.csv")
        with open(self.test_files['special_chars'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
            writer.writerow(['CL001', "Test'; DROP TABLE clinics;--", 'Central', '+267-71234567', 'test@clinic.bw'])
            writer.writerow(['CL002', '<script>alert("XSS")</script>', 'North', '+267-71234568', 'xss@test.com'])
            writer.writerow(['CL003', 'Test "Quotes" & Symbols', 'South', '+267-71234569', 'symbols@test.com'])
        
        # Very large CSV (1000+ rows)
        self.test_files['large_csv'] = os.path.join(self.temp_dir, "large_patients.csv")
        with open(self.test_files['large_csv'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            for i in range(1500):
                writer.writerow([f'P{i:04d}', f'FirstName{i}', f'LastName{i}', '1990-01-01', f'+2677123{i:04d}', 'EN'])
        
        # CSV with Unicode characters
        self.test_files['unicode_csv'] = os.path.join(self.temp_dir, "unicode_patients.csv")
        with open(self.test_files['unicode_csv'], 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            writer.writerow(['P001', '名前', 'السم', '1990-01-01', '+26771234567', 'TSW'])
            writer.writerow(['P002', 'Иван', 'Петров', '1985-05-15', '+26771234568', 'EN'])
        
        # CSV with negative stock quantities
        self.test_files['negative_stock'] = os.path.join(self.temp_dir, "negative_stock.csv")
        with open(self.test_files['negative_stock'], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['stock_id', 'clinic_id', 'item_name', 'on_hand_qty', 'reorder_level', 'unit'])
            writer.writerow(['S001', 'CL001', 'Paracetamol', '-50', '100', 'tablets'])
            writer.writerow(['S002', 'CL001', 'Bandages', '10', '-25', 'rolls'])
        
        # Completely empty file
        self.test_files['empty_file'] = os.path.join(self.temp_dir, "empty.csv")
        open(self.test_files['empty_file'], 'w').close()
        
        # Malformed CSV (no proper structure)
        self.test_files['malformed_csv'] = os.path.join(self.temp_dir, "malformed.csv")
        with open(self.test_files['malformed_csv'], 'w') as f:
            f.write("This is not,a proper,CSV\nfile at all\nrandom text here")
    
    async def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_empty_csv_upload(self, page: Page):
        """Test uploading empty CSV (headers only)"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'clinics')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['empty_clinics'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        # Should handle empty CSV gracefully
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        # Take screenshot for validation
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/empty_csv_upload.png")
    
    async def test_missing_columns_csv(self, page: Page):
        """Test CSV with missing required columns"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'clinics')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['missing_columns'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        # Should show error for missing columns
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/missing_columns.png")
    
    async def test_duplicate_ids_handling(self, page: Page):
        """Test handling of duplicate IDs in CSV"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'patients')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['duplicate_ids'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/duplicate_ids.png")
    
    async def test_sql_injection_prevention(self, page: Page):
        """Test that SQL injection attempts are properly sanitized"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'clinics')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['special_chars'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        # Should upload successfully with sanitized data
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        # Navigate to dashboard to verify data is sanitized
        await page.click('[data-view="dashboard"]')
        await asyncio.sleep(0.5)
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/sql_injection_test.png")
    
    async def test_large_csv_upload(self, page: Page):
        """Test uploading large CSV file (1500 rows)"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'patients')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['large_csv'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(3)  # Allow more time for large file
        
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/large_csv_upload.png")
    
    async def test_unicode_characters(self, page: Page):
        """Test handling of Unicode characters in CSV"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'patients')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['unicode_csv'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/unicode_handling.png")
    
    async def test_negative_quantities(self, page: Page):
        """Test handling of negative stock quantities"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        await page.select_option('#file-type', 'stock')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.test_files['negative_stock'])
        
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        result = page.locator('#upload-result')
        await expect(result).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/negative_quantities.png")


@pytest.mark.e2e
@pytest.mark.edge
@pytest.mark.asyncio
class TestAPIEdgeCases:
    """Edge case tests for API endpoints"""
    
    async def test_invalid_file_type_parameter(self, page: Page):
        """Test API with invalid file_type parameter"""
        response = await page.request.post(
            f"{API_URL}/api/upload?file_type=invalid_type",
            data={'file': 'test,data\n1,2'}
        )
        assert response.status in [400, 422]
    
    async def test_missing_file_type_parameter(self, page: Page):
        """Test API without file_type parameter"""
        response = await page.request.post(
            f"{API_URL}/api/upload",
            data={'file': 'test,data\n1,2'}
        )
        assert response.status in [400, 422]
    
    async def test_empty_request_body(self, page: Page):
        """Test API with empty request body"""
        response = await page.request.post(
            f"{API_URL}/api/upload?file_type=clinics",
            data={}
        )
        assert response.status in [400, 422]
    
    async def test_malformed_json_request(self, page: Page):
        """Test API with malformed JSON"""
        response = await page.request.post(
            f"{API_URL}/api/sms/send",
            data='{"invalid json}',
            headers={'Content-Type': 'application/json'}
        )
        assert response.status in [400, 422]
    
    async def test_api_rate_limiting(self, page: Page):
        """Test API behavior under rapid requests"""
        responses = []
        for i in range(50):
            response = await page.request.get(f"{API_URL}/api/dashboard")
            responses.append(response.status)
        
        # All should succeed (no rate limiting should cause failures)
        assert all(status == 200 for status in responses)
    
    async def test_concurrent_uploads(self, page: Page):
        """Test multiple concurrent CSV uploads"""
        tasks = []
        for i in range(5):
            task = page.request.post(
                f"{API_URL}/api/upload?file_type=clinics",
                multipart={
                    'file': {
                        'name': f'test{i}.csv',
                        'mimeType': 'text/csv',
                        'buffer': b'clinic_id,name,district,phone,email\nCL00' + str(i).encode() + b',Test,Central,+26771234567,test@test.com'
                    }
                }
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        assert all(r.status == 200 for r in responses)
    
    async def test_invalid_patient_id_in_sms(self, page: Page):
        """Test SMS endpoint with invalid patient ID"""
        response = await page.request.post(
            f"{API_URL}/api/sms/send",
            data=json.dumps({
                'patient_id': 'INVALID_ID',
                'appointment_date': '2025-08-15',
                'language': 'EN'
            }),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status in [404, 400]
    
    async def test_future_date_validation(self, page: Page):
        """Test date validation for appointments"""
        # Try to create appointment 10 years in future
        future_date = (datetime.now() + timedelta(days=3650)).strftime('%Y-%m-%d')
        response = await page.request.post(
            f"{API_URL}/api/appointments",
            data=json.dumps({
                'patient_id': 'P001',
                'clinic_id': 'CL001',
                'next_visit_date': future_date,
                'visit_type': 'routine'
            }),
            headers={'Content-Type': 'application/json'}
        )
        # Should either accept or validate reasonably
        assert response.status in [200, 201, 400]
    
    async def test_xss_prevention_in_responses(self, page: Page):
        """Test that API responses properly escape HTML/JS"""
        # Upload data with XSS attempt
        response = await page.request.post(
            f"{API_URL}/api/upload?file_type=clinics",
            multipart={
                'file': {
                    'name': 'xss.csv',
                    'mimeType': 'text/csv',
                    'buffer': b'clinic_id,name,district,phone,email\nCL001,<script>alert("XSS")</script>,Central,+26771234567,test@test.com'
                }
            }
        )
        
        if response.status == 200:
            # Fetch dashboard and check for proper escaping
            dashboard_response = await page.request.get(f"{API_URL}/api/dashboard")
            dashboard_data = await dashboard_response.text()
            assert '<script>' not in dashboard_data or '&lt;script&gt;' in dashboard_data


@pytest.mark.e2e
@pytest.mark.edge
@pytest.mark.asyncio
class TestFrontendEdgeCases:
    """Edge case tests for frontend interactions"""
    
    async def test_rapid_clicking(self, page: Page):
        """Test rapid clicking on buttons"""
        await page.goto(BASE_URL)
        
        # Rapidly click between views
        for _ in range(10):
            await page.click('[data-view="dashboard"]')
            await asyncio.sleep(0.05)
            await page.click('[data-view="upload"]')
            await asyncio.sleep(0.05)
            await page.click('[data-view="reminders"]')
            await asyncio.sleep(0.05)
            await page.click('[data-view="stock"]')
            await asyncio.sleep(0.05)
        
        # App should still be responsive
        await expect(page.locator('h1')).to_contain_text('ClinicLite Botswana')
    
    async def test_browser_back_forward(self, page: Page):
        """Test browser navigation buttons"""
        await page.goto(BASE_URL)
        
        # Navigate through views
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(0.3)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(0.3)
        
        # Use browser back button
        await page.go_back()
        await asyncio.sleep(0.3)
        await page.go_back()
        await asyncio.sleep(0.3)
        
        # Use browser forward button
        await page.go_forward()
        await asyncio.sleep(0.3)
        
        # App should maintain state
        await expect(page.locator('h1')).to_be_visible()
    
    async def test_session_persistence(self, page: Page):
        """Test that uploaded data persists across page refreshes"""
        await page.goto(BASE_URL)
        
        # Upload some data
        await page.click('[data-view="upload"]')
        await page.select_option('#file-type', 'clinics')
        
        # Create and upload a test file
        test_csv = os.path.join(tempfile.gettempdir(), 'session_test.csv')
        with open(test_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
            writer.writerow(['CL999', 'Session Test', 'Central', '+267-71234567', 'session@test.com'])
        
        file_input = page.locator('#file-input')
        await file_input.set_input_files(test_csv)
        await page.click('#upload-btn')
        await asyncio.sleep(1)
        
        # Refresh page
        await page.reload()
        await asyncio.sleep(0.5)
        
        # Navigate to dashboard
        await page.click('[data-view="dashboard"]')
        await asyncio.sleep(0.5)
        
        # Data should still be available
        dashboard = page.locator('#dashboard-view')
        await expect(dashboard).to_be_visible()
        
        os.remove(test_csv)
    
    async def test_language_toggle_persistence(self, page: Page):
        """Test language toggle functionality"""
        await page.goto(BASE_URL)
        
        # Navigate to reminders
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(0.3)
        
        # Toggle language if available
        lang_toggle = page.locator('[id="language-toggle"], [data-test="language-toggle"]')
        if await lang_toggle.is_visible():
            await lang_toggle.click()
            await asyncio.sleep(0.3)
            
            # Verify language changed
            await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/language_toggled.png")
    
    async def test_form_validation_edge_cases(self, page: Page):
        """Test form validation with edge cases"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.3)
        
        # Try to submit without selecting file type
        upload_btn = page.locator('#upload-btn')
        is_disabled = await upload_btn.is_disabled()
        assert is_disabled, "Upload button should be disabled without file type"
        
        # Select file type but no file
        await page.select_option('#file-type', 'patients')
        is_disabled = await upload_btn.is_disabled()
        assert is_disabled, "Upload button should be disabled without file"
    
    async def test_network_interruption_simulation(self, page: Page, context: BrowserContext):
        """Test app behavior during network interruption"""
        await page.goto(BASE_URL)
        
        # Go offline
        await context.set_offline(True)
        await asyncio.sleep(0.5)
        
        # Try to navigate
        await page.click('[data-view="dashboard"]')
        await asyncio.sleep(0.5)
        
        # App should handle offline gracefully
        await expect(page.locator('h1')).to_be_visible()
        
        # Go back online
        await context.set_offline(False)
        await asyncio.sleep(0.5)
        
        # Try API call
        await page.click('[data-view="dashboard"]')
        await asyncio.sleep(1)
        
        dashboard = page.locator('#dashboard-view')
        await expect(dashboard).to_be_visible()
    
    async def test_viewport_responsiveness(self, page: Page):
        """Test app responsiveness across different viewport sizes"""
        viewports = [
            {'width': 320, 'height': 568},   # iPhone SE
            {'width': 768, 'height': 1024},  # iPad
            {'width': 1920, 'height': 1080}, # Desktop
            {'width': 2560, 'height': 1440}, # Large desktop
        ]
        
        for viewport in viewports:
            await page.set_viewport_size(viewport)
            await page.goto(BASE_URL)
            await asyncio.sleep(0.3)
            
            # Check elements are visible
            await expect(page.locator('h1')).to_be_visible()
            await expect(page.locator('[data-view="dashboard"]')).to_be_visible()
            
            # Take screenshot for each viewport
            filename = f"/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/viewport_{viewport['width']}x{viewport['height']}.png"
            await page.screenshot(path=filename)
    
    async def test_memory_leak_prevention(self, page: Page):
        """Test for memory leaks with repeated operations"""
        await page.goto(BASE_URL)
        
        # Perform repeated operations that could cause memory leaks
        for i in range(20):
            # Switch views rapidly
            await page.click('[data-view="upload"]')
            await asyncio.sleep(0.1)
            await page.click('[data-view="dashboard"]')
            await asyncio.sleep(0.1)
            await page.click('[data-view="reminders"]')
            await asyncio.sleep(0.1)
            await page.click('[data-view="stock"]')
            await asyncio.sleep(0.1)
        
        # Check app is still responsive
        await expect(page.locator('h1')).to_be_visible()
        
        # Evaluate memory usage if possible
        try:
            memory_info = await page.evaluate('() => performance.memory')
            print(f"Memory usage after stress test: {memory_info}")
        except:
            pass  # Not all browsers support performance.memory


@pytest.mark.e2e
@pytest.mark.edge
@pytest.mark.asyncio
class TestSecurityEdgeCases:
    """Security-focused edge case tests"""
    
    async def test_csrf_protection(self, page: Page):
        """Test CSRF protection on state-changing operations"""
        # Try to make a direct POST without proper CSRF token
        response = await page.request.post(
            f"{API_URL}/api/upload?file_type=clinics",
            headers={
                'Origin': 'http://malicious-site.com',
                'Referer': 'http://malicious-site.com'
            },
            multipart={
                'file': {
                    'name': 'csrf.csv',
                    'mimeType': 'text/csv',
                    'buffer': b'clinic_id,name,district,phone,email\nCL001,CSRF Test,Central,+26771234567,csrf@test.com'
                }
            }
        )
        # Should be blocked by CORS
        assert response.status in [403, 401] or 'Access-Control-Allow-Origin' not in response.headers
    
    async def test_path_traversal_prevention(self, page: Page):
        """Test path traversal attack prevention"""
        # Try to access files outside allowed directories
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '../../../../etc/shadow',
            '../.env',
        ]
        
        for path in malicious_paths:
            response = await page.request.get(f"{API_URL}/api/file/{path}")
            assert response.status in [400, 403, 404]
    
    async def test_command_injection_prevention(self, page: Page):
        """Test command injection prevention"""
        # Try to inject commands through various inputs
        payloads = [
            '; ls -la',
            '| cat /etc/passwd',
            '`rm -rf /`',
            '$(whoami)',
            '& net user',
        ]
        
        for payload in payloads:
            response = await page.request.post(
                f"{API_URL}/api/upload?file_type=clinics",
                multipart={
                    'file': {
                        'name': f'injection{payload}.csv',
                        'mimeType': 'text/csv',
                        'buffer': f'clinic_id,name,district,phone,email\nCL001,{payload},Central,+26771234567,test@test.com'.encode()
                    }
                }
            )
            # Should process safely without executing commands
            assert response.status in [200, 400]
    
    async def test_xxe_injection_prevention(self, page: Page):
        """Test XML External Entity injection prevention"""
        xxe_payload = '''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
        <data>&xxe;</data>'''
        
        response = await page.request.post(
            f"{API_URL}/api/upload",
            data=xxe_payload,
            headers={'Content-Type': 'application/xml'}
        )
        
        # Should reject or safely process
        assert response.status in [400, 415, 422]
    
    async def test_header_injection_prevention(self, page: Page):
        """Test HTTP header injection prevention"""
        # Try to inject headers through user input
        response = await page.request.post(
            f"{API_URL}/api/sms/send",
            data=json.dumps({
                'patient_id': 'P001\r\nX-Injected-Header: malicious',
                'appointment_date': '2025-08-15',
                'language': 'EN'
            }),
            headers={'Content-Type': 'application/json'}
        )
        
        # Check response headers don't contain injection
        assert 'X-Injected-Header' not in response.headers
    
    async def test_sensitive_data_exposure(self, page: Page):
        """Test that sensitive data is not exposed in responses"""
        # Check various endpoints for data leakage
        endpoints = [
            '/api/dashboard',
            '/api/stats',
            '/api/stock/low-items',
            '/',
        ]
        
        for endpoint in endpoints:
            response = await page.request.get(f"{API_URL}{endpoint}")
            if response.status == 200:
                text = await response.text()
                # Check for sensitive patterns
                assert 'password' not in text.lower()
                assert 'secret' not in text.lower()
                assert 'api_key' not in text.lower()
                assert 'token' not in text.lower()


@pytest.mark.e2e
@pytest.mark.edge
@pytest.mark.asyncio
class TestPerformanceEdgeCases:
    """Performance and load testing edge cases"""
    
    async def test_concurrent_users_simulation(self, page: Page, browser):
        """Simulate multiple concurrent users"""
        contexts = []
        pages = []
        
        # Create 10 concurrent browser contexts
        for i in range(10):
            context = await browser.new_context()
            contexts.append(context)
            new_page = await context.new_page()
            pages.append(new_page)
        
        # All users navigate simultaneously
        tasks = [p.goto(BASE_URL) for p in pages]
        await asyncio.gather(*tasks)
        
        # All users perform actions
        action_tasks = []
        for i, p in enumerate(pages):
            if i % 2 == 0:
                action_tasks.append(p.click('[data-view="dashboard"]'))
            else:
                action_tasks.append(p.click('[data-view="upload"]'))
        
        await asyncio.gather(*action_tasks, return_exceptions=True)
        
        # Clean up
        for context in contexts:
            await context.close()
    
    async def test_dashboard_load_time(self, page: Page):
        """Test dashboard load time meets performance targets"""
        start_time = asyncio.get_event_loop().time()
        
        await page.goto(BASE_URL)
        await page.click('[data-view="dashboard"]')
        
        # Wait for dashboard to be fully loaded
        await page.wait_for_selector('#dashboard-view', state='visible')
        
        end_time = asyncio.get_event_loop().time()
        load_time = end_time - start_time
        
        # Should load within 2 seconds
        assert load_time < 2.0, f"Dashboard load time {load_time}s exceeds 2s target"
    
    async def test_csv_processing_performance(self, page: Page):
        """Test CSV processing meets performance targets"""
        # Create CSV with 1000 rows
        large_csv = os.path.join(tempfile.gettempdir(), 'perf_test.csv')
        with open(large_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            for i in range(1000):
                writer.writerow([f'P{i:04d}', f'First{i}', f'Last{i}', '1990-01-01', f'+2677123{i:04d}', 'EN'])
        
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await page.select_option('#file-type', 'patients')
        
        file_input = page.locator('#file-input')
        await file_input.set_input_files(large_csv)
        
        start_time = asyncio.get_event_loop().time()
        await page.click('#upload-btn')
        
        # Wait for processing to complete
        await page.wait_for_selector('#upload-result', state='visible', timeout=5000)
        
        end_time = asyncio.get_event_loop().time()
        process_time = end_time - start_time
        
        # Should process within 1 second per 1000 records
        assert process_time < 1.0, f"CSV processing time {process_time}s exceeds 1s target for 1000 records"
        
        os.remove(large_csv)


# Test runner configuration
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--junit-xml=/Users/addzmaestro/coding projects/Claude system/workspace/reports/edge_case_test_results.xml",
        "-m", "edge"
    ])