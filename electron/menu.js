const { Menu, ipcMain } = require("electron");

function createMenu(mainWindow) {
    const template = [
        {
            label: "User",
            submenu: []
        },
        {
            label: "History",
            submenu: []
        },
        {
            label: "ETL",
            submenu: [
                {
                    label: "Create new ETL pipeline",
                    click: () => {
                        if (mainWindow) {
                            mainWindow.webContents.send("navigate", "/create-etl");
                        }
                    }
                },
                {
                    label: "My pipelines",
                    click: () => {
                        if (mainWindow) {
                            mainWindow.webContents.send("navigate", "/my-pipelines");
                        }
                    }
                },
                {
                    label: "Help",
                    click: () => {
                        if (mainWindow) {
                            mainWindow.webContents.send("navigate", "/help");
                        }
                    }
                }
            ]
        },
        {
            label: "Settings",
            submenu: []
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

module.exports = { createMenu };
