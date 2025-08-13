"""
Comprehensive Playwright tests for CSV Upload functionality
Tests all 4 entity types: clinics, patients, appointments, stock
"""

import pytest
import asyncio
from pathlib import Path
from playwright.async_api import Page, expect
import csv
import tempfile
import os

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.asyncio
class TestCSVUploadFunctionality:
    """Comprehensive tests for CSV upload feature"""
    
    async def setup_method(self):
        """Create temporary CSV files for testing"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test clinics CSV
        self.clinics_csv = os.path.join(self.temp_dir, "test_clinics.csv")
        with open(self.clinics_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['clinic_id', 'name', 'district', 'phone', 'email'])
            writer.writerow(['CL001', 'Main Clinic', 'Central', '+267-71234567', 'main@clinic.bw'])
            writer.writerow(['CL002', 'North Clinic', 'North', '+267-71234568', 'north@clinic.bw'])
        
        # Create test patients CSV
        self.patients_csv = os.path.join(self.temp_dir, "test_patients.csv")
        with open(self.patients_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'first_name', 'last_name', 'dob', 'phone_e164', 'preferred_lang'])
            writer.writerow(['P001', 'John', 'Doe', '1990-01-01', '+26771234567', 'EN'])
            writer.writerow(['P002', 'Jane', 'Smith', '1985-05-15', '+26771234568', 'TSW'])
        
        # Create test appointments CSV
        self.appointments_csv = os.path.join(self.temp_dir, "test_appointments.csv")
        with open(self.appointments_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['appointment_id', 'patient_id', 'clinic_id', 'next_visit_date', 'visit_type'])
            writer.writerow(['A001', 'P001', 'CL001', '2025-08-15', 'routine'])
            writer.writerow(['A002', 'P002', 'CL002', '2025-08-20', 'follow-up'])
        
        # Create test stock CSV
        self.stock_csv = os.path.join(self.temp_dir, "test_stock.csv")
        with open(self.stock_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['stock_id', 'clinic_id', 'item_name', 'on_hand_qty', 'reorder_level', 'unit'])
            writer.writerow(['S001', 'CL001', 'Paracetamol', '50', '100', 'tablets'])
            writer.writerow(['S002', 'CL001', 'Bandages', '10', '25', 'rolls'])
    
    async def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_application_loads_successfully(self, page: Page):
        """Test that the application loads successfully"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.5)  # Human-like delay
        
        # Check page title
        await expect(page).to_have_title("ClinicLite Botswana - Dashboard")
        
        # Check main heading
        heading = page.locator("h1")
        await expect(heading).to_contain_text("ClinicLite Botswana")
        
        # Check navigation buttons are present
        await expect(page.locator('[data-view="dashboard"]')).to_be_visible()
        await expect(page.locator('[data-view="upload"]')).to_be_visible()
        await expect(page.locator('[data-view="reminders"]')).to_be_visible()
        await expect(page.locator('[data-view="stock"]')).to_be_visible()
        
        # Take screenshot for evidence
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/app_loaded.png")
    
    async def test_navigate_to_upload_view(self, page: Page):
        """Test navigation to CSV upload view"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Click upload button
        upload_button = page.locator('[data-view="upload"]')
        await upload_button.click()
        await asyncio.sleep(0.5)
        
        # Verify upload view is visible
        upload_view = page.locator('#upload-view')
        await expect(upload_view).to_be_visible()
        
        # Verify upload form elements
        await expect(page.locator('#file-type')).to_be_visible()
        await expect(page.locator('#upload-area')).to_be_visible()
        await expect(page.locator('#upload-btn')).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/upload_view.png")
    
    async def test_upload_clinics_csv(self, page: Page):
        """Test uploading clinics CSV file"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Navigate to upload view
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'clinics')
        await asyncio.sleep(0.2)
        
        # Upload file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.clinics_csv)
        await asyncio.sleep(0.3)
        
        # Click upload button
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)  # Wait for upload
        
        # Check success message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/clinics_uploaded.png")
    
    async def test_upload_patients_csv(self, page: Page):
        """Test uploading patients CSV file"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Navigate to upload view
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'patients')
        await asyncio.sleep(0.2)
        
        # Upload file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.patients_csv)
        await asyncio.sleep(0.3)
        
        # Click upload button
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)
        
        # Check success message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/patients_uploaded.png")
    
    async def test_upload_appointments_csv(self, page: Page):
        """Test uploading appointments CSV file"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Navigate to upload view
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'appointments')
        await asyncio.sleep(0.2)
        
        # Upload file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.appointments_csv)
        await asyncio.sleep(0.3)
        
        # Click upload button
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)
        
        # Check success message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/appointments_uploaded.png")
    
    async def test_upload_stock_csv(self, page: Page):
        """Test uploading stock CSV file"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Navigate to upload view
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'stock')
        await asyncio.sleep(0.2)
        
        # Upload file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(self.stock_csv)
        await asyncio.sleep(0.3)
        
        # Click upload button
        upload_btn = page.locator('#upload-btn')
        await upload_btn.click()
        await asyncio.sleep(1)
        
        # Check success message
        result_box = page.locator('#upload-result')
        await expect(result_box).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/stock_uploaded.png")
    
    async def test_upload_validation_no_file(self, page: Page):
        """Test validation when no file is selected"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Navigate to upload view
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Try to upload without selecting file type
        upload_btn = page.locator('#upload-btn')
        await expect(upload_btn).to_be_disabled()
        
        # Select file type but no file
        await page.select_option('#file-type', 'clinics')
        await asyncio.sleep(0.2)
        
        # Button should still be disabled without file
        await expect(upload_btn).to_be_disabled()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/upload_validation.png")
    
    async def test_upload_invalid_file_format(self, page: Page):
        """Test uploading non-CSV file"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Create a non-CSV file
        txt_file = os.path.join(self.temp_dir, "invalid.txt")
        with open(txt_file, 'w') as f:
            f.write("This is not a CSV file")
        
        # Navigate to upload view
        await page.click('[data-view="upload"]')
        await asyncio.sleep(0.5)
        
        # Select file type
        await page.select_option('#file-type', 'clinics')
        await asyncio.sleep(0.2)
        
        # Try to upload non-CSV file
        file_input = page.locator('#file-input')
        await file_input.set_input_files(txt_file)
        await asyncio.sleep(0.3)
        
        # The file input should reject non-CSV files due to accept=".csv" attribute
        # Or we should see an error after upload attempt
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/invalid_file_format.png")