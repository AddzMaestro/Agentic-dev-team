"""Debug test to see what's happening with the prediction page"""
from playwright.sync_api import sync_playwright
import time

def test_debug_prediction_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Try different URLs - corrected paths
        urls = [
            "http://localhost:8000/static/prediction.html",
            "http://localhost:8000/static/test-predictions.html",
            "http://localhost:8000/static/waitlist-management.html",
            "http://localhost:8000/static/sms-monitor.html"
        ]
        
        for url in urls:
            print(f"\nTrying URL: {url}")
            try:
                response = page.goto(url, wait_until="networkidle", timeout=10000)
                print(f"  Status: {response.status if response else 'No response'}")
                print(f"  Title: {page.title()}")
                print(f"  URL: {page.url}")
                
                # Take screenshot
                screenshot_name = url.replace("http://localhost:8000/", "").replace("/", "_")
                page.screenshot(path=f"workspace/reports/screenshots/debug_{screenshot_name}.png")
                
                # Check for error messages
                body_text = page.text_content("body")
                if body_text:
                    print(f"  Body preview: {body_text[:200]}")
                    
            except Exception as e:
                print(f"  Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    test_debug_prediction_page()