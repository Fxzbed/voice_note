import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import DashboardPage from '../views/DashboardPage.vue'
import NotesViewer from '../views/NotesViewer.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import OssTest from '@/views/OssTest.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage
  },
  {
    path: '/notes',
    name: 'Notes',
    component: NotesViewer
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage
  },
  {
    path: '/test',
    name: 'osstest',
    component: OssTest
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
