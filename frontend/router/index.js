import { createRouter, createWebHistory } from 'vue-router'
import Store from '@/store'
import HomePage from '@/pages/HomePage.vue'
import StudyPage from '@/pages/StudyPage.vue'
import CoursePage from '@/pages/CoursePage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { public: true },
  },
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },
  {
    path: '/study',
    name: 'study',
    component: StudyPage,
  },
  {
    path: '/courses/:id',
    name: 'course',
    component: CoursePage,
    props: true,
  },
  {
    path: '/people/:id',
    name: 'profile',
    component: ProfilePage,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const isPublic = to.meta.public === true
  const loggedIn = !!Store.state.user

  if (!isPublic && !loggedIn) {
    next({ name: 'login' })
    return
  }

  if (isPublic && loggedIn && (to.name === 'login' || to.name === 'register')) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
