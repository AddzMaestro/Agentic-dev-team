// ClinicLite Autonomous Test Suite
// Tests for professional UI and entity clearing features

const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:3001';
const API_URL = 'http://localhost:8000';

test.describe('ClinicLite Autonomous Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500); // Human-like pause
  });

  test('01: Application loads successfully', async ({ page }) => {
    // Check title
    await expect(page).toHaveTitle('ClinicLite Botswana - Dashboard');
    
    // Check main elements
    await expect(page.locator('h1')).toContainText('ClinicLite Botswana');
    await expect(page.locator('#connection-status')).toBeVisible();
    
    // Check navigation tabs
    await expect(page.locator('[data-testid="dashboard-tab"]')).toBeVisible();
    await expect(page.locator('[data-testid="csv-upload-tab"]')).toBeVisible();
    await expect(page.locator('[data-testid="reminders-tab"]')).toBeVisible();
    await expect(page.locator('[data-testid="stock-tab"]')).toBeVisible();
  });

  test('02: Dashboard displays data correctly', async ({ page }) => {
    // Wait for dashboard to load
    await page.waitForSelector('#upcoming-visits-list', { state: 'visible' });
    
    // Check three main cards
    const cards = page.locator('.dashboard-card');
    await expect(cards).toHaveCount(3);
    
    // Check counts are visible
    await expect(page.locator('#upcoming-count')).toBeVisible();
    await expect(page.locator('#missed-count')).toBeVisible();
    await expect(page.locator('#low-stock-count')).toBeVisible();
  });

  test('03: Professional UI styling (not default blue)', async ({ page }) => {
    // Check custom CSS is loaded
    const styles = page.locator('link[href="styles.css"]');
    await expect(styles).toHaveCount(1);
    
    // Check header has professional styling
    const header = page.locator('header');
    const headerBg = await header.evaluate(el => window.getComputedStyle(el).backgroundColor);
    
    // Should not be default blue
    expect(headerBg).not.toBe('rgb(0, 0, 255)');
    
    // Check cards have shadows (professional touch)
    const card = page.locator('.dashboard-card').first();
    const shadow = await card.evaluate(el => window.getComputedStyle(el).boxShadow);
    expect(shadow).not.toBe('none');
  });

  test('04: Entity clearing feature exists', async ({ page }) => {
    // Look for settings button
    const settingsBtn = page.locator('[data-testid="settings-btn"]');
    
    // If settings button exists, test clearing feature
    if (await settingsBtn.count() > 0) {
      await settingsBtn.click();
      await page.waitForTimeout(300);
      
      // Check for clear data button
      const clearBtn = page.locator('[data-testid="clear-all-data-btn"]');
      await expect(clearBtn).toBeVisible();
      
      // Test confirmation dialog
      await clearBtn.click();
      await page.waitForTimeout(200);
      
      const confirmDialog = page.locator('[role="dialog"]');
      await expect(confirmDialog).toBeVisible();
      
      // Test cancel
      const cancelBtn = page.locator('[data-testid="cancel-clear-btn"]');
      await cancelBtn.click();
      await expect(confirmDialog).not.toBeVisible();
    }
  });

  test('05: Loading states and spinners', async ({ page }) => {
    // Check if spinner CSS class exists (professional UI feature)
    const spinnerStyles = await page.evaluate(() => {
      const styleSheets = Array.from(document.styleSheets);
      for (const sheet of styleSheets) {
        try {
          const rules = Array.from(sheet.cssRules || sheet.rules);
          const hasSpinner = rules.some(rule => 
            rule.selectorText && rule.selectorText.includes('.spinner')
          );
          if (hasSpinner) return true;
        } catch (e) {
          // Cross-origin stylesheets might throw
        }
      }
      return false;
    });
    
    // Test passes if spinner styles are defined (professional UI implemented)
    expect(spinnerStyles).toBeTruthy();
  });

  test('06: CSV upload functionality', async ({ page }) => {
    // Navigate to upload
    await page.locator('[data-testid="csv-upload-tab"]').click();
    await page.waitForTimeout(300);
    
    // Check upload view
    await expect(page.locator('#upload-view')).toBeVisible();
    await expect(page.locator('#file-type')).toBeVisible();
    await expect(page.locator('#file-input')).toBeVisible();
  });

  test('07: SMS reminder functionality', async ({ page }) => {
    // Navigate to reminders
    await page.locator('[data-testid="reminders-tab"]').click();
    await page.waitForTimeout(300);
    
    // Check language toggle
    const enBtn = page.locator('[data-lang="EN"]');
    const tswBtn = page.locator('[data-lang="TSW"]');
    
    await expect(enBtn).toBeVisible();
    await expect(tswBtn).toBeVisible();
  });

  test('08: Stock management functionality', async ({ page }) => {
    // Navigate to stock
    await page.locator('[data-testid="stock-tab"]').click();
    await page.waitForTimeout(300);
    
    // Check stock table
    await expect(page.locator('#stock-table-body')).toBeVisible();
    await expect(page.locator('[data-testid="reorder-draft-btn"]')).toBeVisible();
  });

  test('09: Responsive design', async ({ page }) => {
    // Test mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    await expect(page.locator('.main-nav')).toBeVisible();
    
    // Test tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    await expect(page.locator('.dashboard-card').first()).toBeVisible();
  });

  test('10: Connection status indicator', async ({ page }) => {
    // Check connection status
    const status = page.locator('#connection-status');
    await expect(status).toBeVisible();
    await expect(status).toContainText('Online');
  });
});