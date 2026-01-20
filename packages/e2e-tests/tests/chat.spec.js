const { test, expect } = require('@playwright/test');

test.describe('Chat Interface', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('page loads with title', async ({ page }) => {
        await expect(page).toHaveTitle('lsimons-agent');
        await expect(page.locator('h1')).toContainText('lsimons-agent');
    });

    test('simple chat response', async ({ page }) => {
        // Type a message
        await page.fill('#message-input', 'how are you');
        await page.click('#send-btn');

        // Wait for response
        await expect(page.locator('.message.agent')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('.message.agent')).toContainText("I'm doing well");
    });

    test('hello world scenario with tool calls', async ({ page }) => {
        // Clear any previous state
        await page.click('button:has-text("Clear")');

        // Type hello world message
        await page.fill('#message-input', 'hello world');
        await page.click('#send-btn');

        // Wait for tool calls to appear
        await expect(page.locator('.message.tool').first()).toBeVisible({ timeout: 10000 });

        // Should show write_file tool call
        await expect(page.locator('.message.tool').first()).toContainText('write_file');

        // Should show bash tool call
        await expect(page.locator('.message.tool').nth(1)).toBeVisible({ timeout: 10000 });
        await expect(page.locator('.message.tool').nth(1)).toContainText('bash');

        // Should show final response
        await expect(page.locator('.message.agent').last()).toContainText('Done');
    });

    test('clear button resets conversation', async ({ page }) => {
        // Send a message
        await page.fill('#message-input', 'how are you');
        await page.click('#send-btn');
        await expect(page.locator('.message.agent')).toBeVisible({ timeout: 10000 });

        // Clear
        await page.click('button:has-text("Clear")');

        // Messages should be cleared
        await expect(page.locator('.message')).toHaveCount(0);
    });
});
