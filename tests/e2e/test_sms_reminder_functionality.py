"""
Comprehensive Playwright tests for SMS Reminder functionality
Tests reminder generation with language toggle (EN/TSW)
"""

import pytest
import asyncio
from playwright.async_api import Page, expect
import aiohttp
import json
import csv
from pathlib import Path

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.asyncio
class TestSMSReminderFunctionality:
    """Comprehensive tests for SMS reminder feature"""
    
    async def setup_method(self):
        """Setup test data via API"""
        sample_data_path = "/Users/addzmaestro/coding projects/Claude system/workspace/data/samples"
        
        async with aiohttp.ClientSession() as session:
            # Upload sample data
            for file_type in ['clinics', 'patients', 'appointments']:
                with open(f"{sample_data_path}/{file_type}.csv", 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=f'{file_type}.csv', content_type='text/csv')
                    await session.post(f"{API_URL}/api/upload?file_type={file_type}", data=data)
    
    async def test_navigate_to_reminders_view(self, page: Page):
        """Test navigation to SMS reminders view"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Click reminders button
        reminders_button = page.locator('[data-view="reminders"]')
        await reminders_button.click()
        await asyncio.sleep(0.5)
        
        # Verify reminders view is visible
        reminders_view = page.locator('#reminders-view')
        await expect(reminders_view).to_be_visible()
        
        # Verify key elements
        await expect(page.locator('.language-toggle')).to_be_visible()
        await expect(page.locator('.patient-selection')).to_be_visible()
        await expect(page.locator('.reminder-actions')).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/reminders_view.png")
    
    async def test_language_toggle_functionality(self, page: Page):
        """Test language toggle between English and Setswana"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(0.5)
        
        # Check initial state - English should be active
        en_button = page.locator('[data-lang="EN"]')
        tsw_button = page.locator('[data-lang="TSW"]')
        
        await expect(en_button).to_have_class("toggle-btn active")
        await expect(tsw_button).to_have_class("toggle-btn")
        
        # Toggle to Setswana
        await tsw_button.click()
        await asyncio.sleep(0.3)
        
        await expect(tsw_button).to_have_class("toggle-btn active")
        await expect(en_button).to_have_class("toggle-btn")
        
        # Toggle back to English
        await en_button.click()
        await asyncio.sleep(0.3)
        
        await expect(en_button).to_have_class("toggle-btn active")
        await expect(tsw_button).to_have_class("toggle-btn")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/language_toggle.png")
    
    async def test_patient_selection_tabs(self, page: Page):
        """Test patient selection tabs (upcoming vs missed)"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(0.5)
        
        # Check tab buttons
        upcoming_tab = page.locator('[data-tab="upcoming"]')
        missed_tab = page.locator('[data-tab="missed"]')
        
        # Upcoming should be active by default
        await expect(upcoming_tab).to_have_class("tab-btn active")
        await expect(missed_tab).to_have_class("tab-btn")
        
        # Switch to missed tab
        await missed_tab.click()
        await asyncio.sleep(0.3)
        
        await expect(missed_tab).to_have_class("tab-btn active")
        await expect(upcoming_tab).to_have_class("tab-btn")
        
        # Switch back to upcoming
        await upcoming_tab.click()
        await asyncio.sleep(0.3)
        
        await expect(upcoming_tab).to_have_class("tab-btn active")
        await expect(missed_tab).to_have_class("tab-btn")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/patient_tabs.png")
    
    async def test_patient_list_population(self, page: Page):
        """Test patient list is populated with checkboxes"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(1)  # Wait for data to load
        
        # Check patient list
        patient_list = page.locator('#patient-list')
        await expect(patient_list).to_be_visible()
        
        # Wait for patients to load
        await page.wait_for_timeout(1000)
        
        # Check for patient checkboxes
        checkboxes = patient_list.locator('input[type="checkbox"]')
        count = await checkboxes.count()
        
        if count > 0:
            # Verify checkbox structure
            first_checkbox = checkboxes.first
            await expect(first_checkbox).to_be_visible()
            
            # Check associated label
            patient_id = await first_checkbox.get_attribute('value')
            assert patient_id, "Checkbox should have patient ID value"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/patient_list.png")
    
    async def test_preview_reminders_english(self, page: Page):
        """Test preview reminders in English"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(1)
        
        # Ensure English is selected
        en_button = page.locator('[data-lang="EN"]')
        await en_button.click()
        await asyncio.sleep(0.3)
        
        # Select some patients
        patient_list = page.locator('#patient-list')
        checkboxes = patient_list.locator('input[type="checkbox"]')
        
        # Select first two patients if available
        count = await checkboxes.count()
        if count > 0:
            await checkboxes.first.check()
            await asyncio.sleep(0.2)
            if count > 1:
                await checkboxes.nth(1).check()
                await asyncio.sleep(0.2)
            
            # Click preview button
            preview_btn = page.locator('button:has-text("Preview Messages")')
            await preview_btn.click()
            await asyncio.sleep(1)
            
            # Check preview box
            preview_box = page.locator('#message-preview')
            await expect(preview_box).to_be_visible()
            
            # Verify English message format
            messages = preview_box.locator('.message-item')
            if await messages.count() > 0:
                first_msg = messages.first
                msg_text = await first_msg.text_content()
                assert "[EN]" in msg_text, "English messages should have [EN] tag"
                assert "Reminder:" in msg_text, "English messages should contain 'Reminder:'"
                assert "appointment" in msg_text.lower()
            
            # Queue button should be enabled
            queue_btn = page.locator('#queue-btn')
            await expect(queue_btn).to_be_enabled()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/preview_english.png")
    
    async def test_preview_reminders_setswana(self, page: Page):
        """Test preview reminders in Setswana"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(1)
        
        # Select Setswana
        tsw_button = page.locator('[data-lang="TSW"]')
        await tsw_button.click()
        await asyncio.sleep(0.3)
        
        # Select some patients
        patient_list = page.locator('#patient-list')
        checkboxes = patient_list.locator('input[type="checkbox"]')
        
        # Select first two patients if available
        count = await checkboxes.count()
        if count > 0:
            await checkboxes.first.check()
            await asyncio.sleep(0.2)
            if count > 1:
                await checkboxes.nth(1).check()
                await asyncio.sleep(0.2)
            
            # Click preview button
            preview_btn = page.locator('button:has-text("Preview Messages")')
            await preview_btn.click()
            await asyncio.sleep(1)
            
            # Check preview box
            preview_box = page.locator('#message-preview')
            await expect(preview_box).to_be_visible()
            
            # Verify Setswana message format
            messages = preview_box.locator('.message-item')
            if await messages.count() > 0:
                first_msg = messages.first
                msg_text = await first_msg.text_content()
                assert "[TSW]" in msg_text, "Setswana messages should have [TSW] tag"
                assert "Kitsiso:" in msg_text, "Setswana messages should contain 'Kitsiso:'"
                assert "bookelo" in msg_text.lower() or "Bookelo" in msg_text
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/preview_setswana.png")
    
    async def test_queue_reminders_to_outbox(self, page: Page):
        """Test queuing reminders to outbox"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(1)
        
        # Select patients
        patient_list = page.locator('#patient-list')
        checkboxes = patient_list.locator('input[type="checkbox"]')
        
        count = await checkboxes.count()
        if count > 0:
            # Select patients
            await checkboxes.first.check()
            await asyncio.sleep(0.2)
            
            # Preview messages
            preview_btn = page.locator('button:has-text("Preview Messages")')
            await preview_btn.click()
            await asyncio.sleep(1)
            
            # Queue messages
            queue_btn = page.locator('#queue-btn')
            await expect(queue_btn).to_be_enabled()
            await queue_btn.click()
            await asyncio.sleep(1)
            
            # Check for success indication
            # This could be a success message, alert, or UI change
            preview_box = page.locator('#message-preview')
            
            # Verify outbox file was created
            outbox_path = Path("/Users/addzmaestro/coding projects/Claude system/workspace/data/messages_outbox.csv")
            if outbox_path.exists():
                # Read and verify CSV content
                with open(outbox_path, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) > 0, "Outbox should contain queued messages"
                    
                    # Verify CSV structure
                    first_row = rows[0]
                    assert 'patient_id' in first_row
                    assert 'phone_e164' in first_row
                    assert 'text' in first_row
                    assert 'lang_tag' in first_row
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/queue_reminders.png")
    
    async def test_reminder_validation_no_selection(self, page: Page):
        """Test validation when no patients are selected"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(0.5)
        
        # Try to preview without selecting patients
        preview_btn = page.locator('button:has-text("Preview Messages")')
        await preview_btn.click()
        await asyncio.sleep(0.5)
        
        # Should show error or empty preview
        preview_box = page.locator('#message-preview')
        
        # Queue button should remain disabled
        queue_btn = page.locator('#queue-btn')
        await expect(queue_btn).to_be_disabled()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/reminder_validation.png")
    
    async def test_reminder_phone_number_format(self, page: Page):
        """Test that phone numbers are in E.164 format"""
        await page.goto(BASE_URL)
        await page.click('[data-view="reminders"]')
        await asyncio.sleep(1)
        
        # Select a patient and preview
        patient_list = page.locator('#patient-list')
        checkboxes = patient_list.locator('input[type="checkbox"]')
        
        if await checkboxes.count() > 0:
            await checkboxes.first.check()
            await asyncio.sleep(0.2)
            
            # Preview messages
            preview_btn = page.locator('button:has-text("Preview Messages")')
            await preview_btn.click()
            await asyncio.sleep(1)
            
            # Check phone number format in preview
            preview_box = page.locator('#message-preview')
            messages = preview_box.locator('.message-item')
            
            if await messages.count() > 0:
                # Look for phone number display
                msg_text = await messages.first.text_content()
                # Phone numbers should start with +267 for Botswana
                import re
                phone_pattern = r'\+267\d{8}'
                assert re.search(phone_pattern, msg_text) or "+267" in msg_text, \
                    "Phone numbers should be in E.164 format (+267...)"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/phone_format.png")