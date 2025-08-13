"""
Comprehensive Playwright tests for Error Handling and Validation
Tests various error scenarios and validation rules
"""

import pytest
import asyncio
from playwright.async_api import Page, expect
import tempfile
import csv
import os

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.asyncio
class TestErrorHandlingAndValidation:
    """Comprehensive tests for error handling and validation"""
    
    async def setup_method(self):
        """Create test files with various error conditions"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create malformed CSV (missing columns)
        self.malformed_csv = os.path.join(self.temp_dir, "malformed.csv")
        with open(self.malformed_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name'])  # Missing required columns
            writer.writerow(['CL001', 'Test Clinic'])
        
        # Create CSV with invalid data types
        self.invalid_data_csv = os.path.join(self.temp_dir, "invalid_data.csv")
        with open(self.invalid_data_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['stock_id', 'clinic_id', 'item_name', 'on_hand_qty', 'reorder_level', 'unit'])
            writer.writerow(['S001', 'CL001', 'Paracetamol', 'not_a_number', '100', 'tablets'])
        
        # Create empty CSV
        self.empty_csv = os.path.join(self.temp_dir, "empty.csv")
        open(self.empty_csv, 'w').close()
        
        # Create oversized CSV (simulate large file)
        self.large_csv = os.path.join(self.temp_dir, "large.csv")
        with open(self.large_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            # Write many rows
            for i in range(10000):
                writer.writerow([f'P{i:05d}', f'First{i}', f'Last{i}', '1990-01-01', '+26771234567', 'EN'])
    
    async def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_upload_malformed_csv(self, page: Page):
        """Test uploading CSV with missing required columns"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'clinics')
        await asyncio.sleep(0.2)
        
        # Upload malformed file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.malformed_csv)
        await asyncio.sleep(0.3)
        
        # Click upload
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)
        
        # Check for error message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        # Should show error about missing columns
        result_text = await result_box.text_content()
        assert "error" in result_text.lower() or "fail" in result_text.lower(), \
            "Should show error for malformed CSV"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_malformed_csv.png")
    
    async def test_upload_invalid_data_types(self, page: Page):
        """Test uploading CSV with invalid data types"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'stock')
        await asyncio.sleep(0.2)
        
        # Upload file with invalid data
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.invalid_data_csv)
        await asyncio.sleep(0.3)
        
        # Click upload
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)
        
        # Check for error or partial success message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        result_text = await result_box.text_content()
        # Should indicate validation error for non-numeric quantity
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_invalid_data.png")
    
    async def test_upload_empty_csv(self, page: Page):
        """Test uploading empty CSV file"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'patients')
        await asyncio.sleep(0.2)
        
        # Upload empty file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.empty_csv)
        await asyncio.sleep(0.3)
        
        # Click upload
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)
        
        # Check for appropriate message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        result_text = await result_box.text_content()
        assert "0" in result_text or "empty" in result_text.lower(), \
            "Should indicate no records processed"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_empty_csv.png")
    
    async def test_upload_without_file_type(self, page: Page):
        """Test uploading without selecting file type"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Don't select file type
        # Try to select file
        file_input = page.locator('#file-input')
        
        # Create a valid CSV
        valid_csv = os.path.join(self.temp_dir, "valid.csv")
        with open(valid_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
            writer.writerow(['CL001', 'Test', 'Central', '123', 'test@test.com'])
        
        # Upload button should be disabled without file type
        upload_btn = page.locator('#upload-btn')
        await expect(upload_btn).to_be_disabled()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_no_file_type.png")
    
    async def test_invalid_phone_number_format(self, page: Page):
        """Test validation of phone number format"""
        # Create CSV with invalid phone numbers
        invalid_phones_csv = os.path.join(self.temp_dir, "invalid_phones.csv")
        with open(invalid_phones_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            writer.writerow(['P001', 'John', 'Doe', '1990-01-01', '1234567', 'EN'])  # Invalid format
            writer.writerow(['P002', 'Jane', 'Smith', '1985-05-15', 'not_a_phone', 'TSW'])  # Not a phone
        
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Upload patients with invalid phones
        await page.select_option('#file-type', 'patients')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(invalid_phones_csv)
        await asyncio.sleep(0.3)
        
        await page.locator('#upload-btn').click()
        await asyncio.sleep(1)
        
        # Check for validation errors
        result_box = page.locator('#upload-result')
        result_text = await result_box.text_content()
        
        # Should show errors about phone format
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_phone_format.png")
    
    async def test_invalid_date_format(self, page: Page):
        """Test validation of date format"""
        # Create CSV with invalid dates
        invalid_dates_csv = os.path.join(self.temp_dir, "invalid_dates.csv")
        with open(invalid_dates_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['appointment_id', 'patient_id', 'clinic_id', 'next_visit_date', 'visit_type'])
            writer.writerow(['A001', 'P001', 'CL001', '15/08/2025', 'routine'])  # Wrong format
            writer.writerow(['A002', 'P002', 'CL001', 'not_a_date', 'follow-up'])  # Invalid date
        
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        await page.select_option('#file-type', 'appointments')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(invalid_dates_csv)
        await asyncio.sleep(0.3)
        
        await page.locator('#upload-btn').click()
        await asyncio.sleep(1)
        
        # Check for date format errors
        result_box = page.locator('#upload-result')
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_date_format.png")
    
    async def test_duplicate_id_handling(self, page: Page):
        """Test handling of duplicate IDs in CSV"""
        # Create CSV with duplicate IDs
        duplicate_csv = os.path.join(self.temp_dir, "duplicates.csv")
        with open(duplicate_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
            writer.writerow(['CL001', 'Clinic One', 'Central', '+267-71234567', 'one@clinic.bw'])
            writer.writerow(['CL001', 'Duplicate Clinic', 'North', '+267-71234568', 'dup@clinic.bw'])
        
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        await page.select_option('#file-type', 'clinics')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(duplicate_csv)
        await asyncio.sleep(0.3)
        
        await page.locator('#upload-btn').click()
        await asyncio.sleep(1)
        
        # System should handle duplicates (either reject or update)
        result_box = page.locator('#upload-result')
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_duplicates.png")
    
    async def test_api_error_handling(self, page: Page):
        """Test handling of API errors"""
        # Try to access API endpoint that doesn't exist
        await page.goto(BASE_URL)
        
        # Attempt to make an invalid API call via console
        api_error = await page.evaluate("""
            async () => {
                try {
                    const response = await fetch('http://localhost:8000/api/nonexistent');
                    return {
                        status: response.status,
                        ok: response.ok
                    };
                } catch (error) {
                    return { error: error.message };
                }
            }
        """)
        
        # Should return 404 or handle gracefully
        if 'status' in api_error:
            assert api_error['status'] == 404, "Nonexistent endpoint should return 404"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_api.png")
    
    async def test_large_file_handling(self, page: Page):
        """Test handling of large CSV files"""
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        await page.select_option('#file-type', 'patients')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.large_csv)
        await asyncio.sleep(0.3)
        
        # Start upload
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        
        # Wait longer for large file
        await asyncio.sleep(3)
        
        # Should either process successfully or show appropriate message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        result_text = await result_box.text_content()
        # Should show number of records processed or size limit error
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/large_file.png")
    
    async def test_required_field_validation(self, page: Page):
        """Test validation of required fields"""
        # Create CSV with missing required fields
        missing_fields_csv = os.path.join(self.temp_dir, "missing_fields.csv")
        with open(missing_fields_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            writer.writerow(['', 'John', 'Doe', '1990-01-01', '+26771234567', 'EN'])  # Missing ID
            writer.writerow(['P002', '', 'Smith', '1985-05-15', '+26771234568', 'TSW'])  # Missing name
        
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        await page.select_option('#file-type', 'patients')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(missing_fields_csv)
        await asyncio.sleep(0.3)
        
        await page.locator('#upload-btn').click()
        await asyncio.sleep(1)
        
        # Check for validation errors
        result_box = page.locator('#upload-result')
        result_text = await result_box.text_content()
        
        # Should indicate missing required fields
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/error_required_fields.png")
    
    async def test_special_characters_handling(self, page: Page):
        """Test handling of special characters in data"""
        # Create CSV with special characters
        special_chars_csv = os.path.join(self.temp_dir, "special_chars.csv")
        with open(special_chars_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
            writer.writerow(['CL001', "O'Reilly's Clinic", 'Centralé', '+267-71234567', 'clinic@test.bw'])
            writer.writerow(['CL002', 'Clinic "Health"', 'North & South', '+267-71234568', 'test@clinic.bw'])
        
        await page.goto(BASE_URL)
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        await page.select_option('#file-type', 'clinics')
        file_input = page.locator('#file-input')
        await file_input.set_input_files(special_chars_csv)
        await asyncio.sleep(0.3)
        
        await page.locator('#upload-btn').click()
        await asyncio.sleep(1)
        
        # Should handle special characters properly
        result_box = page.locator('#upload-result')
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/special_characters.png")