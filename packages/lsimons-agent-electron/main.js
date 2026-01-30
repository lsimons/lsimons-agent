const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');

let serverProcess = null;
let mainWindow = null;

const SERVER_URL = 'http://127.0.0.1:8765';
const PROJECT_ROOT = path.join(__dirname, '..', '..');

function checkServer(url) {
    return new Promise((resolve) => {
        const req = http.get(url, () => {
            resolve(true);
        });
        req.on('error', () => {
            resolve(false);
        });
        req.setTimeout(2000, () => {
            req.destroy();
            resolve(false);
        });
    });
}

async function startServer() {
    // Check if server is already running
    if (await checkServer(SERVER_URL)) {
        console.log('Web server already running');
        return;
    }

    console.log('Starting web server...');

    return new Promise((resolve, reject) => {
        serverProcess = spawn('uv', ['run', 'lsimons-agent-web'], {
            cwd: PROJECT_ROOT,
            stdio: ['ignore', 'pipe', 'pipe'],
            shell: true
        });

        serverProcess.stdout.on('data', (data) => {
            console.log(`server: ${data}`);
        });

        serverProcess.stderr.on('data', (data) => {
            console.error(`server error: ${data}`);
        });

        serverProcess.on('close', (code) => {
            console.log(`Server exited with code ${code}`);
            serverProcess = null;
        });

        // Poll for server to be ready
        const startTime = Date.now();
        const timeout = 30000;

        function check() {
            checkServer(SERVER_URL).then((ready) => {
                if (ready) {
                    resolve();
                } else if (serverProcess === null) {
                    // Server process exited - wait a moment then check if another server is running
                    setTimeout(() => {
                        checkServer(SERVER_URL).then((otherServerReady) => {
                            if (otherServerReady) {
                                console.log('Using existing server');
                                resolve();
                            } else {
                                reject(new Error('Server failed to start'));
                            }
                        });
                    }, 500);
                } else if (Date.now() - startTime > timeout) {
                    reject(new Error('Server start timeout'));
                } else {
                    setTimeout(check, 500);
                }
            });
        }

        // Small delay before first check to let server start
        setTimeout(check, 100);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 900,
        height: 700,
        title: 'lsimons-agent',
        show: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    mainWindow.loadURL(SERVER_URL);
    mainWindow.show();
    mainWindow.focus();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(async () => {
    try {
        await startServer();
        createWindow();
    } catch (error) {
        console.error('Failed to start:', error);
        app.quit();
    }
});

app.on('window-all-closed', () => {
    app.quit();
});

// macOS: re-create window when dock icon is clicked
app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('quit', () => {
    if (serverProcess) {
        console.log('Stopping web server...');
        serverProcess.kill();
    }
});
