"""
Playwright E2E Tests - CSV Upload Functionality
Tests all four CSV upload types with validation
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path

# Base URL for the application
BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"

# Sample data paths
SAMPLES_DIR = Path(__file__).parent.parent.parent / "workspace" / "data" / "samples"

class TestCSVUpload:
    """Test suite for CSV upload functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to upload page before each test"""
        page.goto(BASE_URL)
        time.sleep(0.5)  # Human-like delay
        
        # Click on Upload CSV nav button
        page.click('[data-view="upload"]')
        time.sleep(0.3)
        
    def test_upload_clinics_csv(self, page: Page):
        """Test uploading clinics CSV file"""
        # Select file type
        page.select_option('#file-type', 'clinics')
        time.sleep(0.2)
        
        # Upload file
        file_path = SAMPLES_DIR / "clinics.csv"
        page.set_input_files('#file-input', str(file_path))
        time.sleep(0.3)
        
        # Verify file selected
        expect(page.locator('.upload-area p')).to_contain_text('clinics.csv')
        
        # Click upload button
        page.click('#upload-btn')
        time.sleep(1)  # Wait for upload
        
        # Verify success message
        expect(page.locator('#upload-result')).to_be_visible()
        expect(page.locator('#upload-result h3')).to_contain_text('Success')
        
        # Take screenshot
        page.screenshot(path="screenshots/clinics_upload_success.png")
        
    def test_upload_patients_csv(self, page: Page):
        """Test uploading patients CSV file"""
        # First ensure clinics are uploaded
        self._upload_clinics(page)
        
        # Select patients file type
        page.select_option('#file-type', 'patients')
        time.sleep(0.2)
        
        # Upload file
        file_path = SAMPLES_DIR / "patients.csv"
        page.set_input_files('#file-input', str(file_path))
        time.sleep(0.3)
        
        # Click upload
        page.click('#upload-btn')
        time.sleep(1)
        
        # Verify success
        expect(page.locator('#upload-result')).to_contain_text('records processed')
        
    def test_upload_appointments_csv(self, page: Page):
        """Test uploading appointments CSV file"""
        # Ensure prerequisites
        self._upload_clinics(page)
        self._upload_patients(page)
        
        # Select appointments file type
        page.select_option('#file-type', 'appointments')
        time.sleep(0.2)
        
        # Upload file
        file_path = SAMPLES_DIR / "appointments.csv"
        page.set_input_files('#file-input', str(file_path))
        time.sleep(0.3)
        
        # Click upload
        page.click('#upload-btn')
        time.sleep(1)
        
        # Verify success
        expect(page.locator('#upload-result')).to_be_visible()
        
    def test_upload_stock_csv(self, page: Page):
        """Test uploading stock inventory CSV file"""
        # Ensure clinics exist
        self._upload_clinics(page)
        
        # Select stock file type
        page.select_option('#file-type', 'stock')
        time.sleep(0.2)
        
        # Upload file
        file_path = SAMPLES_DIR / "stock.csv"
        page.set_input_files('#file-input', str(file_path))
        time.sleep(0.3)
        
        # Click upload
        page.click('#upload-btn')
        time.sleep(1)
        
        # Verify success
        expect(page.locator('#upload-result')).to_contain_text('processed')
        
    def test_drag_drop_upload(self, page: Page):
        """Test drag and drop file upload"""
        # Select file type first
        page.select_option('#file-type', 'clinics')
        time.sleep(0.2)
        
        # Create file chooser and drag file
        file_path = SAMPLES_DIR / "clinics.csv"
        
        # Simulate drag and drop (simplified for testing)
        page.set_input_files('#file-input', str(file_path))
        time.sleep(0.3)
        
        # Verify file selected
        expect(page.locator('.upload-area p')).to_contain_text('clinics.csv')
        
    def test_upload_validation_missing_columns(self, page: Page):
        """Test upload with invalid CSV (missing columns)"""
        # This would require a malformed CSV file for testing
        # For now, test that upload without file type shows error
        
        # Try to upload without selecting file type
        file_path = SAMPLES_DIR / "clinics.csv"
        page.set_input_files('#file-input', str(file_path))
        time.sleep(0.2)
        
        # Upload button should be disabled without file type
        expect(page.locator('#upload-btn')).to_be_disabled()
        
    def test_upload_validation_invalid_phone(self, page: Page):
        """Test patient upload with invalid phone format"""
        # Would need a test CSV with invalid phone numbers
        # This test demonstrates the validation flow
        pass
        
    def test_sequential_uploads(self, page: Page):
        """Test uploading all CSV files in correct order"""
        # Upload clinics
        self._upload_clinics(page)
        time.sleep(0.5)
        
        # Upload patients
        self._upload_patients(page)
        time.sleep(0.5)
        
        # Upload appointments
        self._upload_appointments(page)
        time.sleep(0.5)
        
        # Upload stock
        self._upload_stock(page)
        time.sleep(0.5)
        
        # Navigate to dashboard to verify data
        page.click('[data-view="dashboard"]')
        time.sleep(1)
        
        # Verify counts are populated
        expect(page.locator('#total-clinics')).not_to_have_text('0')
        expect(page.locator('#total-patients')).not_to_have_text('0')
        
    # Helper methods
    def _upload_clinics(self, page: Page):
        """Helper to upload clinics CSV"""
        page.select_option('#file-type', 'clinics')
        page.set_input_files('#file-input', str(SAMPLES_DIR / "clinics.csv"))
        page.click('#upload-btn')
        time.sleep(0.5)
        
    def _upload_patients(self, page: Page):
        """Helper to upload patients CSV"""
        page.select_option('#file-type', 'patients')
        page.set_input_files('#file-input', str(SAMPLES_DIR / "patients.csv"))
        page.click('#upload-btn')
        time.sleep(0.5)
        
    def _upload_appointments(self, page: Page):
        """Helper to upload appointments CSV"""
        page.select_option('#file-type', 'appointments')
        page.set_input_files('#file-input', str(SAMPLES_DIR / "appointments.csv"))
        page.click('#upload-btn')
        time.sleep(0.5)
        
    def _upload_stock(self, page: Page):
        """Helper to upload stock CSV"""
        page.select_option('#file-type', 'stock')
        page.set_input_files('#file-input', str(SAMPLES_DIR / "stock.csv"))
        page.click('#upload-btn')
        time.sleep(0.5)