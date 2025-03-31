import { createRouter, createWebHashHistory } from "vue-router";
import CreateETLPipeline from "../components/CreateETLPipeline.vue";
import ETLConfig from "../components/ETLConfig.vue";
import History from "../components/Histroy.vue";
import ActivePipelines from "../components/ActivePipelines.vue";
import Settings from "../components/Settings.vue";
import Dashboard from "../components/Dashboard.vue";
import HomeView from "../components/Home.vue";



const routes = [
    { path: "/", component: Dashboard },
    { path: "/create-etl", component: CreateETLPipeline },
    { path: "/etl-config", component: ETLConfig },
    { path: "/history", component: History },
    { path: "/active-pipelines", component: ActivePipelines },
    { path: "/settings", component: Settings },

];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

export default router;
