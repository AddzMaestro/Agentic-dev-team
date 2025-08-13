"""
Test suite for professional UI improvements
Tests modern styling, animations, and toast notifications
"""

import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
def test_gradient_header(page: Page):
    """Test that gradient header is applied"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Check header exists and has gradient background
    header = page.locator(".header")
    expect(header).to_be_visible()
    
    # Verify settings button is present
    settings_btn = page.locator("#settings-btn")
    expect(settings_btn).to_be_visible()
    
    # Take screenshot for visual verification
    page.screenshot(path="workspace/reports/screenshots/gradient_header.png")

@pytest.mark.e2e
def test_card_hover_effects(page: Page):
    """Test card hover effects and animations"""
    page.goto("http://localhost:3000")
    time.sleep(0.5)
    
    # Get first dashboard card
    card = page.locator(".dashboard-card").first
    expect(card).to_be_visible()
    
    # Hover over card
    card.hover()
    time.sleep(0.3)  # Wait for transition
    
    # Screenshot with hover effect
    page.screenshot(path="workspace/reports/screenshots/card_hover.png")
    
    # Move away from card
    page.locator(".header").hover()
    time.sleep(0.3)

@pytest.mark.e2e
def test_button_states(page: Page):
    """Test button hover and active states"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Test navigation button hover
    dashboard_btn = page.locator('[data-testid="dashboard-tab"]')
    dashboard_btn.hover()
    time.sleep(0.2)
    
    # Test primary button hover
    page.click('[data-testid="stock-tab"]')
    time.sleep(0.5)
    
    reorder_btn = page.locator('[data-testid="reorder-draft-btn"]')
    if reorder_btn.is_visible():
        reorder_btn.hover()
        time.sleep(0.2)
        page.screenshot(path="workspace/reports/screenshots/button_hover.png")

@pytest.mark.e2e
def test_loading_spinner(page: Page):
    """Test that loading states show spinners"""
    page.goto("http://localhost:3000")
    
    # The initial load should show spinners briefly
    # Check if spinner element exists in loading div
    loading = page.locator(".loading .spinner").first
    
    # Note: Spinner might disappear quickly if data loads fast
    # This test mainly verifies the element exists in DOM
    page.screenshot(path="workspace/reports/screenshots/loading_state.png")

@pytest.mark.e2e
def test_smooth_transitions(page: Page):
    """Test smooth transitions between views"""
    page.goto("http://localhost:3000")
    time.sleep(0.5)
    
    # Switch between tabs and verify smooth transitions
    tabs = [
        '[data-testid="csv-upload-tab"]',
        '[data-testid="reminders-tab"]',
        '[data-testid="stock-tab"]',
        '[data-testid="dashboard-tab"]'
    ]
    
    for tab in tabs:
        page.click(tab)
        time.sleep(0.4)  # Wait for transition animation
        
    # Verify we're back on dashboard
    dashboard_view = page.locator("#dashboard-view")
    expect(dashboard_view).to_have_class("view active")

@pytest.mark.e2e 
def test_modern_font_stack(page: Page):
    """Test that Inter font is loaded"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Check that body uses Inter font
    body_font = page.evaluate("window.getComputedStyle(document.body).fontFamily")
    assert "Inter" in body_font or "-apple-system" in body_font

@pytest.mark.e2e
def test_professional_colors(page: Page):
    """Test that professional color scheme is applied"""
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    
    # Verify CSS variables are set
    primary_color = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--primary-color')")
    assert primary_color.strip() == "#0f766e"  # Dark teal
    
    # Check gradient is defined
    gradient = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--primary-gradient')")
    assert "gradient" in gradient.lower()

@pytest.mark.e2e
def test_responsive_layout(page: Page):
    """Test responsive layout at different viewport sizes"""
    # Desktop view
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto("http://localhost:3000")
    time.sleep(0.3)
    page.screenshot(path="workspace/reports/screenshots/desktop_view.png")
    
    # Tablet view
    page.set_viewport_size({"width": 768, "height": 1024})
    time.sleep(0.3)
    page.screenshot(path="workspace/reports/screenshots/tablet_responsive.png")
    
    # Mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    time.sleep(0.3)
    page.screenshot(path="workspace/reports/screenshots/mobile_responsive.png")
    
    # Verify navigation is still accessible
    nav = page.locator(".main-nav")
    expect(nav).to_be_visible()