import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(router);
app.mount("#app");

// 💡 Menüből érkező navigációs esemény
window.electron?.ipcRenderer?.on("navigate", (_, route) => {
    console.log("Navigáció Electron menüből:", route);
    router.push(route);
});