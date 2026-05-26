import { createRouter, createWebHistory } from 'vue-router'

import Login from './components/Login.vue'
import Register from './components/Register.vue'
import StudentDashboard from './components/StudentDashboard.vue'
import CompanyDashboard from './components/CompanyDashboard.vue'
import AdminDashboard from './components/AdminDashboard.vue'


const routes = [
  { path: '/', component: Login },
  { path: '/register', component: Register },
  { path: '/student', component: StudentDashboard },
  { path: '/company', component: CompanyDashboard },
  { path: '/admin', component: AdminDashboard },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (!to.meta.requiresAuth) return next()
 
  const token = localStorage.getItem('token')
  const user  = JSON.parse(localStorage.getItem('user') || 'null')
 
  if (!token || !user) return next('/')                          // not logged in
  if (to.meta.role && user.role !== to.meta.role) return next('/') // wrong role
 
  next()
})

export default router