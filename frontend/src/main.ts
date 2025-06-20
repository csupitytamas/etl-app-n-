import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const userStore = useUserStore(pinia)
userStore.loadUser()

app.mount('#app')

window.electron?.ipcRenderer?.on("navigate", (_, route) => {
  router.push(route)
})