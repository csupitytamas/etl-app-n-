import { createRouter, createWebHashHistory } from "vue-router";
import CreateETLPipeline from "../components/CreateETLPipeline.vue";
import Home from "../components/Home.vue";  // Készíts egy főképernyőt!

const routes = [
    { path: "/", component: Home },  // Ne az App.vue legyen az útvonal
    { path: "/create-etl", component: CreateETLPipeline },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes
});

export default router;
