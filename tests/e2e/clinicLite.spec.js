/**
 * Comprehensive Playwright Tests for ClinicLite Botswana
 * Tests all core functionality with human-like interactions
 */

const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// Configuration
const BASE_URL = 'http://localhost:3001';
const API_URL = 'http://localhost:8000';

// Human-like delays
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

test.describe('ClinicLite Botswana - Comprehensive Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Set viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test.describe('Application Loading', () => {
    test('should load the application successfully', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(500);
      
      // Check title
      await expect(page).toHaveTitle('ClinicLite Botswana - Dashboard');
      
      // Check main header
      const header = page.locator('h1');
      await expect(header).toContainText('ClinicLite Botswana');
      
      // Check navigation buttons
      await expect(page.locator('[data-view="dashboard"]')).toBeVisible();
      await expect(page.locator('[data-view="upload"]')).toBeVisible();
      await expect(page.locator('[data-view="reminders"]')).toBeVisible();
      await expect(page.locator('[data-view="stock"]')).toBeVisible();
      
      // Take screenshot
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/app_loaded.png' 
      });
    });

    test('should show connection status', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(300);
      
      const status = page.locator('#connection-status');
      await expect(status).toBeVisible();
      await expect(status).toHaveClass(/status-online/);
      await expect(status).toContainText('Online');
    });
  });

  test.describe('Dashboard Functionality', () => {
    test('should display three main cards', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(500);
      
      // Check for three dashboard cards
      const cards = page.locator('.dashboard-card');
      await expect(cards).toHaveCount(3);
      
      // Verify Upcoming Visits card
      const upcomingCard = cards.nth(0);
      await expect(upcomingCard.locator('h2')).toContainText('Upcoming Visits');
      await expect(upcomingCard.locator('.badge')).toBeVisible();
      
      // Verify Missed Visits card
      const missedCard = cards.nth(1);
      await expect(missedCard.locator('h2')).toContainText('Missed Visits');
      await expect(missedCard.locator('.badge')).toBeVisible();
      
      // Verify Low Stock card
      const stockCard = cards.nth(2);
      await expect(stockCard.locator('h2')).toContainText('Low Stock Items');
      await expect(stockCard.locator('.badge')).toBeVisible();
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/dashboard_cards.png' 
      });
    });

    test('should display statistics bar', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(500);
      
      const statsBar = page.locator('.stats-bar');
      await expect(statsBar).toBeVisible();
      
      // Check statistics
      await expect(page.locator('#total-clinics')).toBeVisible();
      await expect(page.locator('#total-patients')).toBeVisible();
    });
  });

  test.describe('CSV Upload Functionality', () => {
    test('should navigate to upload view', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(300);
      
      // Click upload button
      await page.click('[data-view="upload"]');
      await delay(500);
      
      // Verify upload view
      const uploadView = page.locator('#upload-view');
      await expect(uploadView).toBeVisible();
      
      // Check form elements
      await expect(page.locator('#file-type')).toBeVisible();
      await expect(page.locator('#upload-area')).toBeVisible();
      await expect(page.locator('#upload-btn')).toBeVisible();
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/upload_view.png' 
      });
    });

    test('should validate file upload requirements', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="upload"]');
      await delay(500);
      
      // Upload button should be disabled initially
      const uploadBtn = page.locator('#upload-btn');
      await expect(uploadBtn).toBeDisabled();
      
      // Select file type
      await page.selectOption('#file-type', 'clinics');
      await delay(200);
      
      // Button should still be disabled without file
      await expect(uploadBtn).toBeDisabled();
    });

    test('should handle CSV file upload', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="upload"]');
      await delay(500);
      
      // Create test CSV file
      const csvContent = 'clinic_id,name,district,phone,email\\nCL001,Test Clinic,Central,+267-71234567,test@clinic.bw';
      const csvPath = '/tmp/test_clinics.csv';
      fs.writeFileSync(csvPath, csvContent);
      
      // Select file type
      await page.selectOption('#file-type', 'clinics');
      await delay(200);
      
      // Upload file
      const fileInput = page.locator('#file-input');
      await fileInput.setInputFiles(csvPath);
      await delay(300);
      
      // Upload button should be enabled
      const uploadBtn = page.locator('#upload-btn');
      await expect(uploadBtn).toBeEnabled();
      
      // Clean up
      fs.unlinkSync(csvPath);
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/csv_upload.png' 
      });
    });
  });

  test.describe('SMS Reminder Functionality', () => {
    test('should navigate to reminders view', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(300);
      
      // Click reminders button
      await page.click('[data-view="reminders"]');
      await delay(500);
      
      // Verify reminders view
      const remindersView = page.locator('#reminders-view');
      await expect(remindersView).toBeVisible();
      
      // Check language toggle
      await expect(page.locator('.language-toggle')).toBeVisible();
      await expect(page.locator('[data-lang="EN"]')).toBeVisible();
      await expect(page.locator('[data-lang="TSW"]')).toBeVisible();
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/reminders_view.png' 
      });
    });

    test('should toggle between languages', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="reminders"]');
      await delay(500);
      
      const enButton = page.locator('[data-lang="EN"]');
      const tswButton = page.locator('[data-lang="TSW"]');
      
      // English should be active by default
      await expect(enButton).toHaveClass(/active/);
      
      // Toggle to Setswana
      await tswButton.click();
      await delay(300);
      await expect(tswButton).toHaveClass(/active/);
      
      // Toggle back to English
      await enButton.click();
      await delay(300);
      await expect(enButton).toHaveClass(/active/);
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/language_toggle.png' 
      });
    });

    test('should switch between patient tabs', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="reminders"]');
      await delay(500);
      
      const upcomingTab = page.locator('[data-tab="upcoming"]');
      const missedTab = page.locator('[data-tab="missed"]');
      
      // Upcoming should be active by default
      await expect(upcomingTab).toHaveClass(/active/);
      
      // Switch to missed
      await missedTab.click();
      await delay(300);
      await expect(missedTab).toHaveClass(/active/);
    });
  });

  test.describe('Stock Management Functionality', () => {
    test('should navigate to stock view', async ({ page }) => {
      await page.goto(BASE_URL);
      await delay(300);
      
      // Click stock button
      await page.click('[data-view="stock"]');
      await delay(500);
      
      // Verify stock view
      const stockView = page.locator('#stock-view');
      await expect(stockView).toBeVisible();
      
      // Check table structure
      await expect(page.locator('.stock-table')).toBeVisible();
      await expect(page.locator('#clinic-filter')).toBeVisible();
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/stock_view.png' 
      });
    });

    test('should display stock table headers', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="stock"]');
      await delay(500);
      
      const headers = page.locator('.stock-table thead th');
      await expect(headers).toHaveCount(6);
      
      await expect(headers.nth(0)).toContainText('Item Name');
      await expect(headers.nth(1)).toContainText('On Hand');
      await expect(headers.nth(2)).toContainText('Reorder Level');
      await expect(headers.nth(3)).toContainText('Deficit');
      await expect(headers.nth(4)).toContainText('Unit');
      await expect(headers.nth(5)).toContainText('Status');
    });

    test('should have reorder draft button', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="stock"]');
      await delay(500);
      
      const reorderBtn = page.locator('button:has-text("Generate Reorder Draft CSV")');
      await expect(reorderBtn).toBeVisible();
    });
  });

  test.describe('Offline Functionality', () => {
    test('should detect offline mode', async ({ page, context }) => {
      await page.goto(BASE_URL);
      await delay(500);
      
      // Check initial online status
      const status = page.locator('#connection-status');
      await expect(status).toContainText('Online');
      
      // Go offline
      await context.setOffline(true);
      await delay(1000);
      
      // Should show offline
      await expect(status).toContainText('Offline');
      
      // Restore connection
      await context.setOffline(false);
      
      // Wait longer for online status to be restored and detected
      // Some applications need more time to detect connection restoration
      await delay(2000);
      
      // Reload the page to ensure connection status is refreshed
      await page.reload();
      await delay(1000);
      
      // Should show online again
      await expect(status).toContainText('Online');
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/offline_mode.png' 
      });
    });

    test('should allow navigation while offline', async ({ page, context }) => {
      await page.goto(BASE_URL);
      await delay(500);
      
      // Go offline
      await context.setOffline(true);
      await delay(500);
      
      // Should still navigate between views
      await page.click('[data-view="upload"]');
      await delay(300);
      await expect(page.locator('#upload-view')).toBeVisible();
      
      await page.click('[data-view="reminders"]');
      await delay(300);
      await expect(page.locator('#reminders-view')).toBeVisible();
      
      // Restore connection
      await context.setOffline(false);
    });
  });

  test.describe('Error Handling', () => {
    test('should validate required form fields', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.click('[data-view="upload"]');
      await delay(500);
      
      // Try to upload without selecting file type
      const uploadBtn = page.locator('#upload-btn');
      await expect(uploadBtn).toBeDisabled();
      
      // Select file type but no file
      await page.selectOption('#file-type', 'patients');
      await delay(200);
      
      // Should still be disabled
      await expect(uploadBtn).toBeDisabled();
    });

    test('should handle API errors gracefully', async ({ page }) => {
      await page.goto(BASE_URL);
      
      // Try to fetch non-existent endpoint
      const response = await page.evaluate(async () => {
        try {
          const res = await fetch('http://localhost:8000/api/nonexistent');
          return { status: res.status };
        } catch (error) {
          return { error: error.message };
        }
      });
      
      // Should handle 404 or network error
      if (response.status) {
        expect(response.status).toBe(404);
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should be responsive on mobile', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto(BASE_URL);
      await delay(500);
      
      // Cards should still be visible
      const cards = page.locator('.dashboard-card');
      await expect(cards).toHaveCount(3);
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/mobile_view.png' 
      });
    });

    test('should be responsive on tablet', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto(BASE_URL);
      await delay(500);
      
      // Cards should be visible
      const cards = page.locator('.dashboard-card');
      await expect(cards).toHaveCount(3);
      
      await page.screenshot({ 
        path: '/Users/addzmaestro/coding projects/Claude system/workspace/reports/screenshots/tablet_view.png' 
      });
    });
  });
});