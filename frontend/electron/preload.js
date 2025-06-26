const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    ipcRenderer: {
        on: (channel, func) => ipcRenderer.on(channel, func),
        send: (channel, ...args) => ipcRenderer.send(channel, ...args),
    },
     getToken: () => {
    return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
     },
    setToken: (token) => {
    localStorage.setItem('auth_token', token)
  }
});
