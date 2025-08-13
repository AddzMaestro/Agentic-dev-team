module.exports = {
  // Test timeout
  timeout: 30000,
  
  // Test retries
  retries: 0,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'workspace/reports/playwright-report' }],
    ['junit', { outputFile: 'workspace/reports/test_results.xml' }]
  ],
  
  use: {
    // Base URL for the application
    baseURL: 'http://localhost:3001',
    
    // Viewport size
    viewport: { width: 1280, height: 720 },
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Trace on failure
    trace: 'on-first-retry',
    
    // Headless mode
    headless: process.env.PLAYWRIGHT_HEADLESS !== 'false',
  },
  
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        // Let Playwright use its default managed browser
        // No executablePath specified - uses Playwright's installed version
      },
    },
  ],
};