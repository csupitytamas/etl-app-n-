import { createRouter, createWebHashHistory } from "vue-router";
import CreateETLPipeline from "../components/CreateETLPipeline.vue";
import ETLConfig from "../components/ETLConfig.vue";
import History from "../components/Histroy.vue";
import ActivePipelines from "../components/ActivePipelines.vue";
import Settings from "../components/Settings.vue";
import Dashboard from "../components/Dashboard.vue";
import EditETLConfig from "../components/EditETLConfig.vue";
import Register from "../components/Register.vue";
import Login from "../components/Login.vue";
import {useUserStore} from "../stores/user";
import Logout from '../components/Logout.vue'




const routes = [
    { path: "/", component: Dashboard },
    { path: "/create-etl", component: CreateETLPipeline },
    { path: "/etl-config", component: ETLConfig },
    { path: "/edit-config", component: EditETLConfig},
    { path: "/history", component: History },
    { path: "/active-pipelines", component: ActivePipelines },
    { path: "/settings", component: Settings },
    { path: "/register", component: Register},
    { path: "/login", component: Login },
    { path: "/logout",component: Logout}// Assuming login uses the same component as register

];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (!userStore.user) {
    try {
      await userStore.loadUser()
    } catch (e) {
      // akkor is menj tovább, ha nem sikerült
    }
  }

  const publicPages = ['/login', '/register', '/logout']
  const authRequired = !publicPages.includes(to.path)

  if (authRequired && !userStore.isAuthenticated()) {
    return next('/login')
  }

  next()
})

export default router;
