import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

const app = createApp(App)
app.use(router)
app.mount('#app')
app.use(createPinia())

// 💡 Menüből érkező navigációs esemény
window.electron?.ipcRenderer?.on("navigate", (_, route) => {
    router.push(route);
});