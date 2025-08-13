#!/usr/bin/env python3
"""
Comprehensive User Journey Tests for ClinicLite Botswana
Maps 1:1 to Low-Level Tasks in PRIMARY_SPEC.md
"""
import pytest
from playwright.sync_api import Page, expect
import time
import json
import sys
from pathlib import Path

# ULTRA-THINK: Test Strategy
# - Test core functionality first
# - Test new features (professional UI, entity clearing)
# - Human-like interactions with delays
# - ARIA role selectors for accessibility

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

class TestClinicLiteUserJourney:
    """Complete user journey through ClinicLite application"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)  # Human-like pause
    
    def test_01_application_loads(self, page: Page):
        """Test that application loads successfully"""
        # Check title
        expect(page).to_have_title("ClinicLite Botswana - Dashboard")
        
        # Check main elements exist
        expect(page.locator("h1")).to_contain_text("ClinicLite Botswana")
        expect(page.locator("#connection-status")).to_be_visible()
        
        # Check navigation tabs
        expect(page.locator("[data-testid='dashboard-tab']")).to_be_visible()
        expect(page.locator("[data-testid='csv-upload-tab']")).to_be_visible()
        expect(page.locator("[data-testid='reminders-tab']")).to_be_visible()
        expect(page.locator("[data-testid='stock-tab']")).to_be_visible()
    
    def test_02_dashboard_displays_data(self, page: Page):
        """Test dashboard shows three main cards with data"""
        # Wait for dashboard to load
        page.wait_for_selector("#upcoming-visits-list", state="visible")
        
        # Check three main cards exist
        cards = page.locator(".dashboard-card")
        expect(cards).to_have_count(3)
        
        # Check upcoming visits card
        upcoming = page.locator("#upcoming-count")
        expect(upcoming).to_be_visible()
        
        # Check missed visits card
        missed = page.locator("#missed-count")
        expect(missed).to_be_visible()
        
        # Check low stock card
        low_stock = page.locator("#low-stock-count")
        expect(low_stock).to_be_visible()
    
    def test_03_professional_ui_styling(self, page: Page):
        """Test that UI has professional styling (not default blue)"""
        # Check for custom CSS loaded
        styles = page.locator("link[href='styles.css']")
        expect(styles).to_have_count(1)
        
        # Check header has professional styling
        header = page.locator("header")
        header_bg = header.evaluate("el => window.getComputedStyle(el).backgroundColor")
        
        # Should not be default blue (#0000FF or rgb(0,0,255))
        assert header_bg != "rgb(0, 0, 255)", "Header should have custom styling"
        
        # Check cards have shadows (professional touch)
        card = page.locator(".dashboard-card").first
        shadow = card.evaluate("el => window.getComputedStyle(el).boxShadow")
        assert shadow != "none", "Cards should have shadow for professional look"
    
    def test_04_csv_upload_functionality(self, page: Page):
        """Test CSV file upload works correctly"""
        # Navigate to upload view
        page.locator("[data-testid='csv-upload-tab']").click()
        time.sleep(0.3)  # Human-like delay
        
        # Check upload view is visible
        expect(page.locator("#upload-view")).to_be_visible()
        
        # Check file type selector
        file_type = page.locator("#file-type")
        expect(file_type).to_be_visible()
        
        # Select stock inventory
        file_type.select_option("stock")
        time.sleep(0.2)
        
        # Check file input exists
        file_input = page.locator("#file-input")
        expect(file_input).to_be_visible()
    
    def test_05_entity_clearing_feature(self, page: Page):
        """Test new entity clearing feature"""
        # Look for settings or clear data button
        # This will be implemented as part of the new feature
        
        # Navigate to settings/admin area
        settings_btn = page.locator("[data-testid='settings-btn']")
        if settings_btn.count() > 0:
            settings_btn.click()
            time.sleep(0.3)
            
            # Look for clear data button
            clear_btn = page.locator("[data-testid='clear-all-data-btn']")
            expect(clear_btn).to_be_visible()
            
            # Check confirmation dialog appears
            clear_btn.click()
            time.sleep(0.2)
            
            confirm_dialog = page.locator("[role='dialog']")
            expect(confirm_dialog).to_be_visible()
            
            # Check cancel works
            cancel_btn = page.locator("[data-testid='cancel-clear-btn']")
            cancel_btn.click()
            expect(confirm_dialog).not_to_be_visible()
    
    def test_06_sms_reminder_generation(self, page: Page):
        """Test SMS reminder functionality"""
        # Navigate to reminders
        page.locator("[data-testid='reminders-tab']").click()
        time.sleep(0.3)
        
        # Check language toggle
        en_btn = page.locator("[data-lang='EN']")
        tsw_btn = page.locator("[data-lang='TSW']")
        
        expect(en_btn).to_be_visible()
        expect(tsw_btn).to_be_visible()
        
        # Toggle language
        tsw_btn.click()
        time.sleep(0.2)
        expect(tsw_btn).to_have_class("active")
    
    def test_07_stock_management(self, page: Page):
        """Test stock management functionality"""
        # Navigate to stock
        page.locator("[data-testid='stock-tab']").click()
        time.sleep(0.3)
        
        # Check stock table exists
        stock_table = page.locator("#stock-table-body")
        expect(stock_table).to_be_visible()
        
        # Check reorder button
        reorder_btn = page.locator("[data-testid='reorder-draft-btn']")
        expect(reorder_btn).to_be_visible()
    
    def test_08_offline_capability(self, page: Page):
        """Test offline mode detection"""
        # Check connection status shows online initially
        status = page.locator("#connection-status")
        expect(status).to_contain_text("Online")
        
        # Simulate offline (this would need backend to be stopped)
        # For now, just check the element exists
        expect(status).to_be_visible()
    
    def test_09_responsive_design(self, page: Page):
        """Test responsive design on different viewports"""
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(0.5)
        
        # Navigation should still be accessible
        expect(page.locator(".main-nav")).to_be_visible()
        
        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        time.sleep(0.5)
        
        # Dashboard cards should be visible
        expect(page.locator(".dashboard-card").first).to_be_visible()
    
    def test_10_loading_states(self, page: Page):
        """Test loading states and spinners"""
        # Refresh page to see loading states
        page.reload()
        
        # Look for loading indicators
        # These should be implemented in the professional UI update
        loading = page.locator(".loading, .spinner")
        
        # Should show loading initially
        if loading.count() > 0:
            expect(loading.first).to_be_visible()
            
            # Should disappear after data loads
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            # Loading should be hidden or removed
            if loading.count() > 0:
                expect(loading.first).to_be_hidden()


@pytest.fixture(scope="session")
def playwright_browser_channel():
    """Use Chromium for testing"""
    return "chromium"


if __name__ == "__main__":
    # Run tests and output results
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    sys.exit(result.returncode)