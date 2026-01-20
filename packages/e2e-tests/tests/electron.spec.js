const { test, expect, _electron: electron } = require('@playwright/test');
const path = require('path');

// Get electron executable path from the electron package
const electronPath = require.resolve('electron');
const electronDir = path.dirname(electronPath);
const electronBin = path.join(electronDir, 'cli.js');

test.describe('Electron App', () => {
    let electronApp;
    let page;

    test.beforeAll(async () => {
        // Launch Electron app
        electronApp = await electron.launch({
            args: [path.join(__dirname, '../../electron/main.js')],
            cwd: path.join(__dirname, '../../electron'),
            env: {
                ...process.env,
                NODE_ENV: 'test',
            },
        });

        // Wait for the first window
        page = await electronApp.firstWindow();

        // Wait for the web server to be ready (it's started by electron)
        await page.waitForLoadState('networkidle');
    });

    test.afterAll(async () => {
        if (electronApp) {
            await electronApp.close();
        }
    });

    test('app window opens with correct title', async () => {
        const title = await page.title();
        expect(title).toBe('lsimons-agent');
    });

    test('can send chat message', async () => {
        // Type a message
        await page.fill('#message-input', 'how are you');
        await page.click('#send-btn');

        // Wait for response
        await expect(page.locator('.message.agent')).toBeVisible({ timeout: 15000 });
        await expect(page.locator('.message.agent')).toContainText("I'm doing well");
    });

    test('hello world creates file via tools', async () => {
        // Clear previous conversation
        await page.click('button:has-text("Clear")');

        // Send hello world
        await page.fill('#message-input', 'hello world');
        await page.click('#send-btn');

        // Wait for tool calls
        await expect(page.locator('.message.tool').first()).toBeVisible({ timeout: 15000 });
        await expect(page.locator('.message.tool').first()).toContainText('write_file');

        // Wait for completion
        await expect(page.locator('.message.agent').last()).toContainText('Done', {
            timeout: 15000
        });
    });
});
