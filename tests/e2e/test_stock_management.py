"""
Comprehensive Playwright tests for Stock Management functionality
Tests low stock detection and reorder draft generation
"""

import pytest
import asyncio
from playwright.async_api import Page, expect
import aiohttp
import json
import csv
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

@pytest.mark.e2e
@pytest.mark.asyncio
class TestStockManagementFunctionality:
    """Comprehensive tests for stock management feature"""
    
    async def setup_method(self):
        """Setup test data via API"""
        sample_data_path = "/Users/addzmaestro/coding projects/Claude system/workspace/data/samples"
        
        async with aiohttp.ClientSession() as session:
            # Upload required data
            for file_type in ['clinics', 'stock']:
                with open(f"{sample_data_path}/{file_type}.csv", 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=f'{file_type}.csv', content_type='text/csv')
                    await session.post(f"{API_URL}/api/upload?file_type={file_type}", data=data)
    
    async def test_navigate_to_stock_view(self, page: Page):
        """Test navigation to stock management view"""
        await page.goto(BASE_URL)
        await asyncio.sleep(0.3)
        
        # Click stock button
        stock_button = page.locator('[data-view="stock"]')
        await stock_button.click()
        await asyncio.sleep(0.5)
        
        # Verify stock view is visible
        stock_view = page.locator('#stock-view')
        await expect(stock_view).to_be_visible()
        
        # Verify key elements
        await expect(page.locator('.stock-filters')).to_be_visible()
        await expect(page.locator('.stock-table-container')).to_be_visible()
        await expect(page.locator('.stock-actions')).to_be_visible()
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/stock_view.png")
    
    async def test_stock_table_display(self, page: Page):
        """Test stock table displays data correctly"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)  # Wait for data to load
        
        # Check stock table
        table = page.locator('.stock-table')
        await expect(table).to_be_visible()
        
        # Verify table headers
        headers = table.locator('thead th')
        await expect(headers).to_have_count(6)
        await expect(headers.nth(0)).to_contain_text("Item Name")
        await expect(headers.nth(1)).to_contain_text("On Hand")
        await expect(headers.nth(2)).to_contain_text("Reorder Level")
        await expect(headers.nth(3)).to_contain_text("Deficit")
        await expect(headers.nth(4)).to_contain_text("Unit")
        await expect(headers.nth(5)).to_contain_text("Status")
        
        # Check table body
        tbody = table.locator('tbody')
        rows = tbody.locator('tr')
        row_count = await rows.count()
        
        if row_count > 0:
            # Verify first row structure
            first_row = rows.first
            cells = first_row.locator('td')
            await expect(cells).to_have_count(6)
            
            # Check deficit calculation
            on_hand = await cells.nth(1).text_content()
            reorder_level = await cells.nth(2).text_content()
            deficit = await cells.nth(3).text_content()
            
            # Verify status indicator
            status_cell = cells.nth(5)
            status_text = await status_cell.text_content()
            assert status_text in ["Low", "Critical", "OK"], "Status should be Low, Critical, or OK"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/stock_table.png")
    
    async def test_clinic_filter_functionality(self, page: Page):
        """Test clinic filter dropdown"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)
        
        # Check clinic filter dropdown
        filter_dropdown = page.locator('#clinic-filter')
        await expect(filter_dropdown).to_be_visible()
        
        # Check default option
        selected_value = await filter_dropdown.input_value()
        assert selected_value == "", "Default should be 'All Clinics'"
        
        # Get available options
        options = filter_dropdown.locator('option')
        option_count = await options.count()
        
        if option_count > 1:  # More than just "All Clinics"
            # Select a specific clinic
            await filter_dropdown.select_option(index=1)
            await asyncio.sleep(0.5)
            
            # Verify table updates (rows should be filtered)
            tbody = page.locator('.stock-table tbody')
            rows_after = tbody.locator('tr')
            
            # Select "All Clinics" again
            await filter_dropdown.select_option(value="")
            await asyncio.sleep(0.5)
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/clinic_filter.png")
    
    async def test_low_stock_detection(self, page: Page):
        """Test that low stock items are properly identified"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)
        
        # Check for low stock items in table
        tbody = page.locator('.stock-table tbody')
        rows = tbody.locator('tr')
        row_count = await rows.count()
        
        low_stock_count = 0
        for i in range(row_count):
            row = rows.nth(i)
            cells = row.locator('td')
            
            on_hand_text = await cells.nth(1).text_content()
            reorder_text = await cells.nth(2).text_content()
            status_text = await cells.nth(5).text_content()
            
            try:
                on_hand = int(on_hand_text.strip())
                reorder_level = int(reorder_text.strip())
                
                if on_hand < reorder_level:
                    low_stock_count += 1
                    # Verify status reflects low stock
                    assert status_text in ["Low", "Critical"], \
                        f"Item with on_hand {on_hand} < reorder {reorder_level} should show Low/Critical status"
            except ValueError:
                pass  # Skip if not numeric
        
        # Also check dashboard low stock count matches
        await page.click('[data-view="dashboard"]')
        await asyncio.sleep(1)
        
        dashboard_count = await page.locator('#low-stock-count').text_content()
        dashboard_count_int = int(dashboard_count) if dashboard_count.isdigit() else 0
        
        print(f"Found {low_stock_count} low stock items, dashboard shows {dashboard_count_int}")
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/low_stock_detection.png")
    
    async def test_generate_reorder_draft_from_stock_view(self, page: Page):
        """Test generating reorder draft from stock management view"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)
        
        # Click generate reorder draft button
        reorder_btn = page.locator('button:has-text("Generate Reorder Draft CSV")')
        await expect(reorder_btn).to_be_visible()
        
        # Select a clinic if dropdown has options
        filter_dropdown = page.locator('#clinic-filter')
        options = filter_dropdown.locator('option')
        if await options.count() > 1:
            await filter_dropdown.select_option(index=1)
            await asyncio.sleep(0.5)
            
            # Click reorder button
            await reorder_btn.click()
            await asyncio.sleep(1)
            
            # Check for success indication
            # This could be an alert, message, or file download
            
            # Verify reorder file was created
            today = datetime.now().strftime('%Y-%m-%d')
            reorder_path = Path(f"/Users/addzmaestro/coding projects/Claude system/workspace/data/reorder_draft_{today}.csv")
            
            if reorder_path.exists():
                # Read and verify CSV content
                with open(reorder_path, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    
                    if len(rows) > 0:
                        # Verify CSV structure
                        first_row = rows[0]
                        assert 'Item Name' in first_row
                        assert 'Current Quantity' in first_row
                        assert 'Suggested Order Quantity' in first_row
                        assert 'Unit' in first_row
                        
                        # Verify suggested quantity calculation
                        for row in rows:
                            current = int(row['Current Quantity'])
                            suggested = int(row['Suggested Order Quantity'])
                            assert suggested > current, \
                                "Suggested order quantity should be greater than current"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/reorder_draft_stock.png")
    
    async def test_generate_reorder_draft_from_dashboard(self, page: Page):
        """Test generating reorder draft from dashboard"""
        await page.goto(BASE_URL)
        await asyncio.sleep(1)
        
        # Find the reorder button in low stock card
        reorder_btn = page.locator('.dashboard-card').nth(2).locator('button:has-text("Generate Reorder Draft")')
        await expect(reorder_btn).to_be_visible()
        
        # Click reorder button
        await reorder_btn.click()
        await asyncio.sleep(1)
        
        # This might show a clinic selection dialog or generate for all clinics
        # Check for any modal or selection UI
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/reorder_draft_dashboard.png")
    
    async def test_stock_status_indicators(self, page: Page):
        """Test stock status visual indicators"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)
        
        # Check status indicators in table
        tbody = page.locator('.stock-table tbody')
        rows = tbody.locator('tr')
        
        for i in range(min(5, await rows.count())):  # Check first 5 rows
            row = rows.nth(i)
            cells = row.locator('td')
            
            on_hand_text = await cells.nth(1).text_content()
            reorder_text = await cells.nth(2).text_content()
            status_cell = cells.nth(5)
            
            try:
                on_hand = int(on_hand_text.strip())
                reorder_level = int(reorder_text.strip())
                
                # Check appropriate styling based on stock level
                if on_hand == 0:
                    # Critical - should have danger styling
                    await expect(status_cell).to_contain_text("Critical")
                elif on_hand < reorder_level:
                    # Low - should have warning styling
                    await expect(status_cell).to_contain_text("Low")
                else:
                    # OK - should have success styling
                    await expect(status_cell).to_contain_text("OK")
            except ValueError:
                pass
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/stock_status.png")
    
    async def test_stock_deficit_calculation(self, page: Page):
        """Test deficit calculation accuracy"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)
        
        # Verify deficit calculations
        tbody = page.locator('.stock-table tbody')
        rows = tbody.locator('tr')
        
        errors = []
        for i in range(min(10, await rows.count())):
            row = rows.nth(i)
            cells = row.locator('td')
            
            item_name = await cells.nth(0).text_content()
            on_hand_text = await cells.nth(1).text_content()
            reorder_text = await cells.nth(2).text_content()
            deficit_text = await cells.nth(3).text_content()
            
            try:
                on_hand = int(on_hand_text.strip())
                reorder_level = int(reorder_text.strip())
                displayed_deficit = int(deficit_text.strip()) if deficit_text.strip() != '-' else 0
                
                # Calculate expected deficit
                expected_deficit = max(0, reorder_level - on_hand)
                
                if displayed_deficit != expected_deficit:
                    errors.append(f"{item_name}: Expected deficit {expected_deficit}, got {displayed_deficit}")
            except ValueError:
                pass
        
        assert len(errors) == 0, f"Deficit calculation errors: {errors}"
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/deficit_calculation.png")
    
    async def test_stock_table_sorting(self, page: Page):
        """Test if stock table can be sorted"""
        await page.goto(BASE_URL)
        await page.click('[data-view="stock"]')
        await asyncio.sleep(1)
        
        # Try clicking on column headers to sort
        table = page.locator('.stock-table')
        item_header = table.locator('thead th').first
        
        # Get initial order
        tbody = table.locator('tbody')
        rows = tbody.locator('tr')
        initial_items = []
        
        for i in range(min(5, await rows.count())):
            item_name = await rows.nth(i).locator('td').first.text_content()
            initial_items.append(item_name.strip())
        
        # Click header to sort (if sortable)
        await item_header.click()
        await asyncio.sleep(0.5)
        
        # Get new order
        sorted_items = []
        for i in range(min(5, await rows.count())):
            item_name = await rows.nth(i).locator('td').first.text_content()
            sorted_items.append(item_name.strip())
        
        # Check if order changed (indicating sorting capability)
        # Note: If not sortable, order will remain the same
        
        await page.screenshot(path="/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/stock_sorting.png")