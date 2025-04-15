const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const http = require('http'); //  HTTP kérések küldéséhez
const { createMenu } = require("./menu");

let mainWindow;
const VITE_DEV_SERVER_URL = 'http://localhost:5173';


async function waitForViteServer(retries = 20) {
    return new Promise((resolve) => {
        const checkServer = () => {
            http.get(VITE_DEV_SERVER_URL, () => {
                console.log("✅ Vite szerver elérhető!");
                resolve();
            }).on("error", () => {
                if (retries > 0) {
                    console.log(`⏳ Várakozás a Vite szerverre... (${retries})`);
                    setTimeout(() => checkServer(), 500); // Fél másodpercenként újrapróbáljuk
                } else {
                    console.error("❌ Vite szerver nem indult el időben.");
                    resolve();
                }
            });
        };
        checkServer();
    });
}
// 🖼 **Főablak létrehozása**
async function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    await waitForViteServer(); // 💡 Megvárjuk a Vite szervert
    mainWindow.loadURL(VITE_DEV_SERVER_URL);

    createMenu(mainWindow); // 📌 Menü inicializálása az ablakhoz

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    console.log("🚀 Electron ready!");
    createWindow();
});


app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        app.quit();
    }
});


ipcMain.on("navigate", (_, route) => {
    if (mainWindow) {
        mainWindow.webContents.send("navigate", route);
    }
});
