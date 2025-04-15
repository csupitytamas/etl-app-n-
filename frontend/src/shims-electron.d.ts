export {}

declare global {
    interface Window {
        electron?: {
            ipcRenderer?: {
                on: (channel: string, callback: (event: any, ...args: any[]) => void) => void;
                send: (channel: string, ...args: any[]) => void;
            }
        }
    }
}
