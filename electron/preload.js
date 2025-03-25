const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
    navigate: (route) => ipcRenderer.send("navigate", route),
    onNavigate: (callback) => ipcRenderer.on("navigate", (_, route) => callback(route)),
});