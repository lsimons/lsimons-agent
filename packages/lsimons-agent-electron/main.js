const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');

// Auto-updater (only loaded in packaged builds to avoid dev errors)
let autoUpdater = null;
if (app.isPackaged) {
    try {
        autoUpdater = require('electron-updater').autoUpdater;
    } catch (e) {
        console.error('Failed to load electron-updater:', e);
    }
}

let serverProcess = null;
let mainWindow = null;

const SERVER_URL = 'http://127.0.0.1:8765';
const PROJECT_ROOT = path.join(__dirname, '..', '..');

function getServerCommand() {
    if (app.isPackaged) {
        // In packaged app, use bundled executable
        const ext = process.platform === 'win32' ? '.exe' : '';
        const serverPath = path.join(process.resourcesPath, 'backend', `lsimons-agent-web${ext}`);
        return {
            command: serverPath,
            args: [],
            options: {}
        };
    } else {
        // In development, use uv
        return {
            command: 'uv',
            args: ['run', 'lsimons-agent-web'],
            options: { cwd: PROJECT_ROOT, shell: true }
        };
    }
}

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

    const { command, args, options } = getServerCommand();
    console.log(`Running: ${command} ${args.join(' ')}`);

    return new Promise((resolve, reject) => {
        serverProcess = spawn(command, args, {
            ...options,
            stdio: ['ignore', 'pipe', 'pipe']
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

        serverProcess.on('error', (err) => {
            console.error('Failed to start server:', err);
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

function setupAutoUpdater() {
    if (!autoUpdater) return;

    autoUpdater.on('checking-for-update', () => {
        console.log('Checking for updates...');
    });

    autoUpdater.on('update-available', (info) => {
        console.log('Update available:', info.version);
    });

    autoUpdater.on('update-not-available', () => {
        console.log('No updates available');
    });

    autoUpdater.on('download-progress', (progress) => {
        console.log(`Download progress: ${Math.round(progress.percent)}%`);
    });

    autoUpdater.on('update-downloaded', (info) => {
        dialog.showMessageBox({
            type: 'info',
            title: 'Update Ready',
            message: `Version ${info.version} is ready. Restart to apply?`,
            buttons: ['Restart', 'Later']
        }).then((result) => {
            if (result.response === 0) {
                autoUpdater.quitAndInstall();
            }
        });
    });

    autoUpdater.on('error', (err) => {
        console.error('Auto-update error:', err);
    });

    // Check for updates
    autoUpdater.checkForUpdatesAndNotify();
}

app.whenReady().then(async () => {
    try {
        await startServer();
        createWindow();
        setupAutoUpdater();
    } catch (error) {
        console.error('Failed to start:', error);
        dialog.showErrorBox('Startup Error', error.message);
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
