"""
Comprehensive Playwright tests for Dashboard functionality
Tests dashboard rendering with three cards: upcoming visits, missed visits, low stock
"""

import pytest
import asyncio
from playwright.async_api import Page, expect
import aiohttp
import json

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.asyncio
class TestDashboardFunctionality:
    """Comprehensive tests for dashboard feature"""
    
    async def setup_method(self):
        """Setup test data via API"""
        # First upload sample data files
        sample_data_path = "/Users/addzmaestro/coding projects/Claude system/workspace/data/samples"
        
        async with aiohttp.ClientSession() as session:
            # Upload clinics
            with open(f"{sample_data_path}/clinics.csv", 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='clinics.csv', content_type='text/csv')
                await session.post(f"{API_URL}/api/upload?file_type=clinics", data=data)
            
            # Upload patients
            with open(f"{sample_data_path}/patients.csv", 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='patients.csv', content_type='text/csv')
                await session.post(f"{API_URL}/api/upload?file_type=patients", data=data)
            
            # Upload appointments
            with open(f"{sample_data_path}/appointments.csv", 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='appointments.csv', content_type='text/csv')
                await session.post(f"{API_URL}/api/upload?file_type=appointments", data=data)
            
            # Upload stock
            with open(f"{sample_data_path}/stock.csv", 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='stock.csv', content_type='text/csv')
                await session.post(f"{API_URL}/api/upload?file_type=stock", data=data)
    
    async def test_dashboard_loads_with_three_cards(self, page: Page):
        """Test that dashboard loads with all three main cards"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.5)
        
        # Ensure we're on dashboard view
        dashboard_view = page.locator('#dashboard-view')
        await expect(dashboard_view).to_be_visible()
        await expect(dashboard_view).to_have_class("view active")
        
        # Check for three main cards
        cards = page.locator('.dashboard-card')
        await expect(cards).to_have_count(3)
        
        # Verify Upcoming Visits card
        upcoming_card = cards.nth(0)
        await expect(upcoming_card.locator('h2')).to_contain_text("Upcoming Visits")
        await expect(upcoming_card.locator('.badge')).to_be_visible()
        await expect(upcoming_card.locator('.card-footer small')).to_contain_text("Next 7 days")
        
        # Verify Missed Visits card
        missed_card = cards.nth(1)
        await expect(missed_card.locator('h2')).to_contain_text("Missed Visits")
        await expect(missed_card.locator('.badge')).to_be_visible()
        await expect(missed_card.locator('.card-footer small')).to_contain_text("Past 7 days")
        
        # Verify Low Stock card
        stock_card = cards.nth(2)
        await expect(stock_card.locator('h2')).to_contain_text("Low Stock Items")
        await expect(stock_card.locator('.badge')).to_be_visible()
        await expect(stock_card.locator('button')).to_contain_text("Generate Reorder Draft")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/dashboard_three_cards.png")
    
    async def test_upcoming_visits_display(self, page: Page):
        """Test upcoming visits card displays data correctly"""
        await page.goto(BASE_URL)
        await asyncio.sleep(1)  # Wait for data to load
        
        # Check upcoming visits list
        upcoming_list = page.locator('#upcoming-visits-list')
        await expect(upcoming_list).to_be_visible()
        
        # Wait for loading to finish
        loading = upcoming_list.locator('.loading')
        await expect(loading).to_be_hidden(timeout=5000)
        
        # Check if visits are displayed (or empty message)
        visit_items = upcoming_list.locator('.visit-item')
        count = await visit_items.count()
        
        if count > 0:
            # Verify visit item structure
            first_visit = visit_items.first
            await expect(first_visit).to_be_visible()
            
            # Check badge count matches
            badge = page.locator('#upcoming-count')
            badge_text = await badge.text_content()
            assert int(badge_text) == count
        else:
            # Check for empty state message
            empty_msg = upcoming_list.locator('p')
            await expect(empty_msg).to_contain_text("No upcoming visits")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/upcoming_visits_display.png")
    
    async def test_missed_visits_display(self, page: Page):
        """Test missed visits card displays data correctly"""
        await page.goto(BASE_URL)
        await asyncio.sleep(1)  # Wait for data to load
        
        # Check missed visits list
        missed_list = page.locator('#missed-visits-list')
        await expect(missed_list).to_be_visible()
        
        # Wait for loading to finish
        loading = missed_list.locator('.loading')
        await expect(loading).to_be_hidden(timeout=5000)
        
        # Check if visits are displayed
        visit_items = missed_list.locator('.visit-item')
        count = await visit_items.count()
        
        if count > 0:
            # Verify visit item structure
            first_visit = visit_items.first
            await expect(first_visit).to_be_visible()
            
            # Check badge count matches
            badge = page.locator('#missed-count')
            badge_text = await badge.text_content()
            assert int(badge_text) == count
            
            # Badge should have warning styling
            await expect(badge).to_have_class("badge badge-warning")
        else:
            # Check for empty state message
            empty_msg = missed_list.locator('p')
            await expect(empty_msg).to_contain_text("No missed visits")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/missed_visits_display.png")
    
    async def test_low_stock_items_display(self, page: Page):
        """Test low stock items card displays data correctly"""
        await page.goto(BASE_URL)
        await asyncio.sleep(1)  # Wait for data to load
        
        # Check low stock list
        stock_list = page.locator('#low-stock-list')
        await expect(stock_list).to_be_visible()
        
        # Wait for loading to finish
        loading = stock_list.locator('.loading')
        await expect(loading).to_be_hidden(timeout=5000)
        
        # Check if stock items are displayed
        stock_items = stock_list.locator('.stock-item')
        count = await stock_items.count()
        
        if count > 0:
            # Verify stock item structure
            first_item = stock_items.first
            await expect(first_item).to_be_visible()
            
            # Check badge count matches
            badge = page.locator('#low-stock-count')
            badge_text = await badge.text_content()
            assert int(badge_text) == count
            
            # Badge should have danger styling
            await expect(badge).to_have_class("badge badge-danger")
        else:
            # Check for empty state message
            empty_msg = stock_list.locator('p')
            await expect(empty_msg).to_contain_text("No low stock items")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/low_stock_display.png")
    
    async def test_statistics_bar_display(self, page: Page):
        """Test statistics bar displays correctly"""
        await page.goto(BASE_URL)
        await asyncio.sleep(1)
        
        # Check statistics bar
        stats_bar = page.locator('.stats-bar')
        await expect(stats_bar).to_be_visible()
        
        # Check total clinics stat
        clinics_stat = page.locator('#total-clinics')
        await expect(clinics_stat).to_be_visible()
        clinics_text = await clinics_stat.text_content()
        assert clinics_text.isdigit(), "Clinics count should be a number"
        
        # Check total patients stat
        patients_stat = page.locator('#total-patients')
        await expect(patients_stat).to_be_visible()
        patients_text = await patients_stat.text_content()
        assert patients_text.isdigit(), "Patients count should be a number"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/statistics_bar.png")
    
    async def test_dashboard_data_refresh(self, page: Page):
        """Test dashboard data can be refreshed"""
        await page.goto(BASE_URL)
        await asyncio.sleep(1)
        
        # Get initial counts
        upcoming_count = await page.locator('#upcoming-count').text_content()
        missed_count = await page.locator('#missed-count').text_content()
        stock_count = await page.locator('#low-stock-count').text_content()
        
        # Reload page to refresh data
        await page.reload()
        await asyncio.sleep(1)
        
        # Verify counts are displayed after refresh
        new_upcoming = await page.locator('#upcoming-count').text_content()
        new_missed = await page.locator('#missed-count').text_content()
        new_stock = await page.locator('#low-stock-count').text_content()
        
        assert new_upcoming.isdigit()
        assert new_missed.isdigit()
        assert new_stock.isdigit()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/dashboard_refreshed.png")
    
    async def test_connection_status_indicator(self, page: Page):
        """Test connection status indicator"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.5)
        
        # Check connection status
        status = page.locator('#connection-status')
        await expect(status).to_be_visible()
        await expect(status).to_have_class("status-online")
        await expect(status).to_contain_text("Online")
        
        # Check current date display
        date_display = page.locator('#current-date')
        await expect(date_display).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/connection_status.png")
    
    async def test_dashboard_responsiveness(self, page: Page):
        """Test dashboard is responsive on different screen sizes"""
        # Desktop view
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto(BASE_URL)
        await asyncio.sleep(0.5)
        
        cards = page.locator('.dashboard-card')
        await expect(cards).to_have_count(3)
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/dashboard_desktop.png")
        
        # Tablet view
        await page.set_viewport_size({"width": 768, "height": 1024})
        await asyncio.sleep(0.3)
        await expect(cards).to_have_count(3)
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/dashboard_tablet.png")
        
        # Mobile view
        await page.set_viewport_size({"width": 375, "height": 667})
        await asyncio.sleep(0.3)
        await expect(cards).to_have_count(3)
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/dashboard_mobile.png")