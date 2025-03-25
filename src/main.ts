import { createApp } from "vue";
import App from "./App.vue";
import router from "./router"; // 🔹 Mostmár csak az importált router kell!

const app = createApp(App);
app.use(router);
app.mount("#app");

// 📌 Figyeljük az Electron üzeneteit
window.electron?.ipcRenderer?.on("navigate", (_, route) => {
    router.push(route);
});
