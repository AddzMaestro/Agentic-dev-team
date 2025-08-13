const { chromium } = require('playwright');

(async () => {
  try {
    console.log('Launching Chromium with Playwright 1.38.0...');
    
    const browser = await chromium.launch({
      headless: false, // Set to true for headless mode
    });
    
    const page = await browser.newPage();
    await page.goto('https://example.com');
    console.log('Successfully navigated to:', await page.title());
    
    await browser.close();
    console.log('Test completed successfully!');
  } catch (error) {
    console.error('Error:', error.message);
  }
})();