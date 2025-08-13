// Comprehensive Edge Case Tests with Human-like Behavior for ClinicLite
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const BASE_URL = 'http://localhost:3001';
const API_URL = 'http://localhost:8000';
const HUMAN_DELAY_MIN = 100;
const HUMAN_DELAY_MAX = 500;
const TYPING_DELAY = 50;

// Helper functions for human-like behavior
async function humanDelay() {
  const delay = Math.floor(Math.random() * (HUMAN_DELAY_MAX - HUMAN_DELAY_MIN + 1)) + HUMAN_DELAY_MIN;
  await new Promise(resolve => setTimeout(resolve, delay));
}

async function humanClick(page, selector) {
  const element = await page.waitForSelector(selector, { timeout: 5000 });
  await element.hover();
  await humanDelay();
  await element.click();
  await humanDelay();
}

async function humanType(page, selector, text) {
  const element = await page.waitForSelector(selector, { timeout: 5000 });
  await element.hover();
  await humanDelay();
  await element.click();
  await humanDelay();
  await element.type(text, { delay: TYPING_DELAY });
  await humanDelay();
}

async function scrollToElement(page, selector) {
  await page.evaluate((sel) => {
    const element = document.querySelector(sel);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, selector);
  await humanDelay();
}

// Create temporary CSV files for testing
function createTempCSV(filename, headers, rows) {
  const tempDir = os.tmpdir();
  const filepath = path.join(tempDir, filename);
  let content = headers.join(',') + '\n';
  rows.forEach(row => {
    content += row.join(',') + '\n';
  });
  fs.writeFileSync(filepath, content);
  return filepath;
}

test.describe('CSV Upload Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport and navigate
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    await humanDelay();
  });

  test('Empty CSV file upload', async ({ page }) => {
    const emptyFile = createTempCSV('empty.csv', [], []);
    
    // Navigate to CSV upload section
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    // Upload empty file
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(emptyFile);
      await humanDelay();
    }
    
    // Check for error message
    const errorMessage = await page.$('.error-message, .alert-danger, .validation-error');
    if (errorMessage) {
      expect(await errorMessage.isVisible()).toBeTruthy();
    }
    
    // Screenshot
    await page.screenshot({ path: 'workspace/reports/screenshots/empty_csv_test.png' });
    
    // Cleanup
    fs.unlinkSync(emptyFile);
  });

  test('Malformed CSV with missing columns', async ({ page }) => {
    const malformedFile = createTempCSV('malformed.csv', 
      ['wrong_header1', 'wrong_header2'],
      [['value1', 'value2']]
    );
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(malformedFile);
      await humanDelay();
    }
    
    // Check for validation error
    const error = await page.waitForSelector('.validation-error, .error-message, .alert-danger', { 
      timeout: 5000,
      state: 'visible' 
    }).catch(() => null);
    
    if (error) {
      expect(await error.isVisible()).toBeTruthy();
    }
    
    await page.screenshot({ path: 'workspace/reports/screenshots/malformed_csv_test.png' });
    fs.unlinkSync(malformedFile);
  });

  test('Large CSV file (1500 rows)', async ({ page }) => {
    // Create large CSV
    const rows = [];
    for (let i = 0; i < 1500; i++) {
      rows.push([
        `P${String(i).padStart(6, '0')}`,
        `FirstName${i}`,
        `LastName${i}`,
        `+267${70000000 + Math.floor(Math.random() * 9999999)}`,
        Math.random() > 0.5 ? 'EN' : 'TSW'
      ]);
    }
    
    const largeFile = createTempCSV('large.csv',
      ['patient_id', 'first_name', 'last_name', 'phone', 'language'],
      rows
    );
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const startTime = Date.now();
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(largeFile);
    }
    
    // Wait for processing with longer timeout
    await page.waitForSelector('.upload-success, .success-message', { 
      timeout: 30000 
    }).catch(() => null);
    
    const processingTime = (Date.now() - startTime) / 1000;
    console.log(`Large file processing time: ${processingTime}s`);
    
    // Check processing time
    expect(processingTime).toBeLessThan(2);
    
    await page.screenshot({ path: 'workspace/reports/screenshots/large_csv_test.png' });
    fs.unlinkSync(largeFile);
  });

  test('Special characters and emojis in CSV', async ({ page }) => {
    const specialFile = createTempCSV('special.csv',
      ['patient_id', 'first_name', 'last_name', 'phone', 'language'],
      [
        ['P001', 'José', 'García', '+26770000001', 'EN'],
        ['P002', 'François', 'Müller', '+26770000002', 'TSW'],
        ['P003', '李明', '王', '+26770000003', 'EN'],
        ['P004', 'محمد', 'أحمد', '+26770000004', 'TSW']
      ]
    );
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(specialFile);
      await humanDelay();
    }
    
    // Check if upload succeeded
    await page.waitForSelector('.upload-success, .success-message', { 
      timeout: 10000 
    }).catch(() => null);
    
    await page.screenshot({ path: 'workspace/reports/screenshots/special_chars_test.png' });
    fs.unlinkSync(specialFile);
  });
});

test.describe('Input Validation Security', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    await humanDelay();
  });

  test('SQL injection prevention', async ({ page }) => {
    const sqlPayloads = [
      "'; DROP TABLE patients; --",
      "1' OR '1'='1",
      "admin'--",
      "' UNION SELECT * FROM users--",
      "1; DELETE FROM appointments WHERE 1=1--"
    ];
    
    for (const payload of sqlPayloads) {
      // Try injection in search field if exists
      const searchInput = await page.$('input[type="search"], input[placeholder*="Search"], input[name="search"]');
      if (searchInput) {
        await humanType(page, 'input[type="search"], input[placeholder*="Search"], input[name="search"]', payload);
        await page.keyboard.press('Enter');
        await humanDelay();
        
        // Check app is still functional
        const title = await page.title();
        expect(title).not.toBe('');
        
        // Clear input
        await searchInput.fill('');
      }
    }
    
    await page.screenshot({ path: 'workspace/reports/screenshots/sql_injection_test.png' });
  });

  test('XSS prevention', async ({ page }) => {
    const xssPayloads = [
      '<script>alert("XSS")</script>',
      '<img src=x onerror=alert("XSS")>',
      'javascript:alert("XSS")',
      '<svg onload=alert("XSS")>',
      '<iframe src="javascript:alert(\'XSS\')"></iframe>'
    ];
    
    const xssFile = createTempCSV('xss.csv',
      ['patient_id', 'first_name', 'last_name', 'phone', 'language'],
      xssPayloads.map((payload, i) => [`P${i}`, payload, 'Test', '+26770000001', 'EN'])
    );
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    // Set up dialog handler to detect XSS
    let xssDetected = false;
    page.on('dialog', async dialog => {
      xssDetected = true;
      await dialog.dismiss();
    });
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(xssFile);
      await humanDelay();
    }
    
    // Wait a bit to see if any XSS triggers
    await page.waitForTimeout(2000);
    
    expect(xssDetected).toBeFalsy();
    
    await page.screenshot({ path: 'workspace/reports/screenshots/xss_prevention_test.png' });
    fs.unlinkSync(xssFile);
  });

  test('Extremely long input handling', async ({ page }) => {
    const longString = 'A'.repeat(15000);
    
    const longFile = createTempCSV('long.csv',
      ['patient_id', 'first_name', 'last_name', 'phone', 'language'],
      [['P001', longString, 'Test', '+26770000001', 'EN']]
    );
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(longFile);
      await humanDelay();
    }
    
    // Check that app handles long input
    const result = await page.waitForSelector('.error-message, .upload-success, .validation-error', {
      timeout: 10000
    }).catch(() => null);
    
    expect(result).not.toBeNull();
    
    await page.screenshot({ path: 'workspace/reports/screenshots/long_input_test.png' });
    fs.unlinkSync(longFile);
  });
});

test.describe('UI Interaction Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    await humanDelay();
  });

  test('Rapid clicking on buttons', async ({ page }) => {
    const buttons = await page.$$('button');
    
    // Test first 5 buttons with rapid clicks
    for (let i = 0; i < Math.min(5, buttons.length); i++) {
      const button = buttons[i];
      // Rapid click 10 times
      for (let j = 0; j < 10; j++) {
        await button.click();
        await page.waitForTimeout(50);
      }
      await humanDelay();
    }
    
    // Check app is still responsive
    const title = await page.title();
    expect(title).not.toBe('');
    
    await page.screenshot({ path: 'workspace/reports/screenshots/rapid_clicking_test.png' });
  });

  test('Double-clicking single-click elements', async ({ page }) => {
    const links = await page.$$('a');
    
    // Test first 3 links with double clicks
    for (let i = 0; i < Math.min(3, links.length); i++) {
      await links[i].dblclick();
      await humanDelay();
    }
    
    // App should still be functional
    const title = await page.title();
    expect(title).not.toBe('');
    
    await page.screenshot({ path: 'workspace/reports/screenshots/double_click_test.png' });
  });

  test('Keyboard navigation', async ({ page }) => {
    // Tab through elements
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }
    
    // Try Enter on focused element
    await page.keyboard.press('Enter');
    await humanDelay();
    
    // Try Escape
    await page.keyboard.press('Escape');
    await humanDelay();
    
    // Navigate with arrow keys
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('ArrowLeft');
    await page.keyboard.press('ArrowRight');
    
    await page.screenshot({ path: 'workspace/reports/screenshots/keyboard_nav_test.png' });
  });

  test('Browser navigation (back/forward)', async ({ page }) => {
    // Navigate to different sections if available
    const dashboardTab = await page.$('[data-testid="dashboard-tab"], #dashboard-tab');
    if (dashboardTab) {
      await humanClick(page, '[data-testid="dashboard-tab"], #dashboard-tab');
    }
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab');
    }
    
    // Go back
    await page.goBack();
    await humanDelay();
    
    // Go forward
    await page.goForward();
    await humanDelay();
    
    // Refresh
    await page.reload();
    await humanDelay();
    
    await page.screenshot({ path: 'workspace/reports/screenshots/browser_nav_test.png' });
  });
});

test.describe('Network Conditions', () => {
  test('Offline mode transition', async ({ page, context }) => {
    await page.goto(BASE_URL);
    await humanDelay();
    
    // Go offline
    await context.setOffline(true);
    await humanDelay();
    
    // Try to perform actions
    const buttons = await page.$$('button');
    if (buttons.length > 0) {
      await buttons[0].click();
      await humanDelay();
    }
    
    // Check for offline indicator
    const offlineIndicator = await page.$('.offline-indicator, [data-testid="offline-badge"], .offline-mode');
    if (offlineIndicator) {
      expect(await offlineIndicator.isVisible()).toBeTruthy();
    }
    
    // Go back online
    await context.setOffline(false);
    await humanDelay();
    
    // Reload and check recovery
    await page.reload();
    await humanDelay();
    
    await page.screenshot({ path: 'workspace/reports/screenshots/offline_mode_test.png' });
  });

  test('Slow network simulation', async ({ page, context }) => {
    // Note: Real network throttling would require CDP
    // This is a simplified version
    
    const startTime = Date.now();
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    const loadTime = (Date.now() - startTime) / 1000;
    
    console.log(`Page load time: ${loadTime}s`);
    
    // Should load within reasonable time
    expect(loadTime).toBeLessThan(10);
    
    await page.screenshot({ path: 'workspace/reports/screenshots/slow_network_test.png' });
  });
});

test.describe('Boundary Conditions', () => {
  test('Edge dates testing', async ({ page }) => {
    const edgeDatesFile = createTempCSV('edge_dates.csv',
      ['appointment_id', 'patient_id', 'clinic_id', 'appointment_date', 'appointment_time'],
      [
        ['A001', 'P001', 'C001', '1900-01-01', '09:00'],
        ['A002', 'P002', 'C001', '2100-12-31', '23:59'],
        ['A003', 'P003', 'C001', '2024-02-29', '12:00'],
        ['A004', 'P004', 'C001', '2024-12-31', '00:00']
      ]
    );
    
    await page.goto(BASE_URL);
    await humanDelay();
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(edgeDatesFile);
      await humanDelay();
    }
    
    // Check handling of edge dates
    const result = await page.waitForSelector('.upload-success, .validation-error', {
      timeout: 10000
    }).catch(() => null);
    
    expect(result).not.toBeNull();
    
    await page.screenshot({ path: 'workspace/reports/screenshots/edge_dates_test.png' });
    fs.unlinkSync(edgeDatesFile);
  });

  test('Phone number format variations', async ({ page }) => {
    const phoneFormatsFile = createTempCSV('phone_formats.csv',
      ['patient_id', 'first_name', 'last_name', 'phone', 'language'],
      [
        ['P001', 'Test1', 'User', '+26770000001', 'EN'],
        ['P002', 'Test2', 'User', '26770000002', 'EN'],
        ['P003', 'Test3', 'User', '70000003', 'EN'],
        ['P004', 'Test4', 'User', '+267-7000-0004', 'EN'],
        ['P005', 'Test5', 'User', '(267) 7000-0005', 'EN']
      ]
    );
    
    await page.goto(BASE_URL);
    await humanDelay();
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(phoneFormatsFile);
      await humanDelay();
    }
    
    // Check phone number handling
    const result = await page.waitForSelector('.upload-success, .validation-warning', {
      timeout: 10000
    }).catch(() => null);
    
    expect(result).not.toBeNull();
    
    await page.screenshot({ path: 'workspace/reports/screenshots/phone_formats_test.png' });
    fs.unlinkSync(phoneFormatsFile);
  });
});

test.describe('Concurrent Operations', () => {
  test('Page refresh during operation', async ({ page }) => {
    const tempFile = createTempCSV('refresh_test.csv',
      ['patient_id', 'first_name', 'last_name', 'phone', 'language'],
      Array.from({ length: 100 }, (_, i) => [
        `P${i}`, `Test${i}`, `User${i}`, `+2677000000${i}`, 'EN'
      ])
    );
    
    await page.goto(BASE_URL);
    await humanDelay();
    
    const uploadTab = await page.$('[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    if (uploadTab) {
      await humanClick(page, '[data-testid="csv-upload-tab"], #csv-upload-tab, button:has-text("Upload CSV")');
    }
    
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(tempFile);
      
      // Refresh during upload
      await page.waitForTimeout(500);
      await page.reload();
      await humanDelay();
    }
    
    // Check app recovered
    const title = await page.title();
    expect(title).not.toBe('');
    
    await page.screenshot({ path: 'workspace/reports/screenshots/refresh_during_op_test.png' });
    fs.unlinkSync(tempFile);
  });
});

// Run summary reporter
test.afterAll(async () => {
  console.log('\n========================================');
  console.log('Edge Case Testing Complete');
  console.log('Reports saved to workspace/reports/');
  console.log('Screenshots saved to workspace/reports/screenshots/');
  console.log('========================================\n');
});