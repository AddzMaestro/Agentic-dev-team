"""
Test suite for data clearing feature
Tests settings modal, confirmation dialog, and clear all data functionality
"""

import pytest
from playwright.sync_api import Page, expect
import time
import requests

@pytest.mark.e2e
def test_settings_button_visible(page: Page):
    """Test that settings button is visible in header"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    settings_btn = page.locator("#settings-btn")
    expect(settings_btn).to_be_visible()
    expect(settings_btn).to_have_attribute("aria-label", "Settings")
    
    # Take screenshot
    page.screenshot(path="workspace/reports/screenshots/settings_button.png")

@pytest.mark.e2e
def test_settings_modal_opens(page: Page):
    """Test that clicking settings button opens modal"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Click settings button
    page.click("#settings-btn")
    time.sleep(0.3)  # Wait for animation
    
    # Verify modal is visible
    modal = page.locator('[data-testid="settings-modal"]')
    expect(modal).to_have_class("modal active")
    
    # Verify modal content
    modal_header = modal.locator("h2")
    expect(modal_header).to_have_text("Settings")
    
    # Verify clear data button is present
    clear_btn = page.locator('[data-testid="clear-all-data-btn"]')
    expect(clear_btn).to_be_visible()
    expect(clear_btn).to_contain_text("Clear All Data")
    
    page.screenshot(path="workspace/reports/screenshots/settings_modal_open.png")

@pytest.mark.e2e
def test_settings_modal_close_button(page: Page):
    """Test that X button closes settings modal"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Open modal
    page.click("#settings-btn")
    time.sleep(0.3)
    
    # Click close button
    page.click("#close-settings")
    time.sleep(0.3)
    
    # Verify modal is closed
    modal = page.locator('[data-testid="settings-modal"]')
    expect(modal).not_to_have_class("modal active")

@pytest.mark.e2e
def test_settings_modal_backdrop_close(page: Page):
    """Test that clicking backdrop closes modal"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Open modal
    page.click("#settings-btn")
    time.sleep(0.3)
    
    # Click on backdrop (outside modal content)
    modal = page.locator('[data-testid="settings-modal"]')
    modal.click(position={"x": 10, "y": 10})  # Click near edge
    time.sleep(0.3)
    
    # Verify modal is closed
    expect(modal).not_to_have_class("modal active")

@pytest.mark.e2e
def test_confirmation_dialog_opens(page: Page):
    """Test that clicking Clear All Data opens confirmation dialog"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Open settings modal
    page.click("#settings-btn")
    time.sleep(0.3)
    
    # Click Clear All Data button
    page.click('[data-testid="clear-all-data-btn"]')
    time.sleep(0.3)
    
    # Verify confirmation dialog is visible
    confirm_dialog = page.locator('[data-testid="confirm-dialog"]')
    expect(confirm_dialog).to_have_class("modal active")
    
    # Verify dialog content
    dialog_header = confirm_dialog.locator("h3")
    expect(dialog_header).to_have_text("Confirm Data Deletion")
    
    # Verify warning text
    warning = confirm_dialog.locator(".warning-text").first
    expect(warning).to_contain_text("Are you sure?")
    
    # Verify list of items to be deleted
    deletion_list = confirm_dialog.locator(".deletion-list li")
    expect(deletion_list).to_have_count(4)
    
    # Verify buttons
    cancel_btn = page.locator('[data-testid="cancel-clear"]')
    confirm_btn = page.locator('[data-testid="confirm-clear"]')
    expect(cancel_btn).to_be_visible()
    expect(confirm_btn).to_be_visible()
    
    page.screenshot(path="workspace/reports/screenshots/confirmation_dialog.png")

@pytest.mark.e2e
def test_cancel_clear_data(page: Page):
    """Test that cancel button closes dialog without clearing data"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Open settings and confirmation dialog
    page.click("#settings-btn")
    time.sleep(0.3)
    page.click('[data-testid="clear-all-data-btn"]')
    time.sleep(0.3)
    
    # Click cancel
    page.click('[data-testid="cancel-clear"]')
    time.sleep(0.3)
    
    # Verify dialog is closed
    confirm_dialog = page.locator('[data-testid="confirm-dialog"]')
    expect(confirm_dialog).not_to_have_class("modal active")
    
    # Verify data is still present (check dashboard counts)
    # This assumes there's existing data - might need to upload first

@pytest.mark.e2e
def test_clear_all_data_flow(page: Page):
    """Test complete flow of clearing all data"""
    page.goto("http://localhost:3000")
    time.sleep(0.5)
    
    # First, upload some test data to ensure we have something to clear
    page.click('[data-testid="csv-upload-tab"]')
    time.sleep(0.3)
    
    # Note: This test assumes sample data exists
    # In a real test, we would upload CSV files first
    
    # Go back to dashboard
    page.click('[data-testid="dashboard-tab"]')
    time.sleep(0.3)
    
    # Open settings modal
    page.click("#settings-btn")
    time.sleep(0.3)
    
    # Click Clear All Data
    page.click('[data-testid="clear-all-data-btn"]')
    time.sleep(0.3)
    
    # Confirm deletion
    page.click('[data-testid="confirm-clear"]')
    time.sleep(1)  # Wait for API call
    
    # Verify success toast appears
    toast = page.locator(".toast.success")
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("All data cleared successfully")
    
    # Verify modals are closed
    settings_modal = page.locator('[data-testid="settings-modal"]')
    confirm_dialog = page.locator('[data-testid="confirm-dialog"]')
    expect(settings_modal).not_to_have_class("modal active")
    expect(confirm_dialog).not_to_have_class("modal active")
    
    # Verify dashboard counts are reset to 0
    upcoming_count = page.locator("#upcoming-count")
    missed_count = page.locator("#missed-count")
    low_stock_count = page.locator("#low-stock-count")
    
    expect(upcoming_count).to_have_text("0")
    expect(missed_count).to_have_text("0")
    expect(low_stock_count).to_have_text("0")
    
    page.screenshot(path="workspace/reports/screenshots/data_cleared.png")

@pytest.mark.e2e
def test_clear_data_api_endpoint():
    """Test the DELETE /api/clear-all-data endpoint directly"""
    # First, check current data status
    stats_response = requests.get("http://localhost:8000/api/stats")
    assert stats_response.status_code == 200
    initial_stats = stats_response.json()
    
    # Call clear data endpoint
    clear_response = requests.delete("http://localhost:8000/api/clear-all-data")
    assert clear_response.status_code == 200
    
    # Verify response structure
    data = clear_response.json()
    assert data["status"] == "success"
    assert "cleared" in data
    assert "clinics" in data["cleared"]
    assert "patients" in data["cleared"]
    assert "appointments" in data["cleared"]
    assert "stock" in data["cleared"]
    
    # Verify all data is cleared
    stats_after = requests.get("http://localhost:8000/api/stats").json()
    assert stats_after["total_clinics"] == 0
    assert stats_after["total_patients"] == 0
    assert stats_after["total_appointments"] == 0
    assert stats_after["stock_items"] == 0

@pytest.mark.e2e
def test_toast_auto_dismiss(page: Page):
    """Test that toast notifications auto-dismiss after 3 seconds"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Trigger an action that shows a toast
    # For this test, we'll use the clear data flow
    page.click("#settings-btn")
    time.sleep(0.3)
    page.click('[data-testid="clear-all-data-btn"]')
    time.sleep(0.3)
    page.click('[data-testid="confirm-clear"]')
    time.sleep(0.5)
    
    # Verify toast appears
    toast = page.locator(".toast").first
    expect(toast).to_be_visible()
    
    # Wait for auto-dismiss (3 seconds + animation)
    time.sleep(3.5)
    
    # Verify toast is gone
    toast_count = page.locator(".toast").count()
    assert toast_count == 0

@pytest.mark.e2e
def test_toast_manual_close(page: Page):
    """Test that toast can be manually closed"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Trigger a toast
    page.click("#settings-btn")
    time.sleep(0.3)
    page.click('[data-testid="clear-all-data-btn"]')
    time.sleep(0.3)
    page.click('[data-testid="confirm-clear"]')
    time.sleep(0.5)
    
    # Find and click toast close button
    toast = page.locator(".toast").first
    expect(toast).to_be_visible()
    
    close_btn = toast.locator(".toast-close")
    close_btn.click()
    time.sleep(0.3)  # Wait for animation
    
    # Verify toast is gone
    expect(toast).not_to_be_visible()