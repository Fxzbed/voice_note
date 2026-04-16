import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import UploadView from "../views/UploadView.vue";
import TaskListView from "../views/TaskListView.vue";
import TaskDetailView from "../views/TaskDetailView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/login" },
    { path: "/login", component: LoginView },
    { path: "/upload", component: UploadView },
    { path: "/tasks", component: TaskListView },
    { path: "/tasks/:id", component: TaskDetailView },
  ],
});

export default router;