const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
    testDir: './tests',
    timeout: 60000,
    expect: {
        timeout: 10000
    },
    projects: [
        {
            name: 'web',
            testMatch: 'chat.spec.js',
            use: {
                baseURL: 'http://localhost:8765',
            },
        },
        {
            name: 'electron',
            testMatch: 'electron.spec.js',
        },
    ],
    webServer: [
        {
            command: 'uv run mock-llm-server',
            cwd: '../..',
            port: 8000,
            reuseExistingServer: true,
        },
        {
            command: 'uv run lsimons-agent-web',
            cwd: '../..',
            port: 8765,
            reuseExistingServer: true,
        }
    ],
});
