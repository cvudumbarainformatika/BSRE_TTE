const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('pages/auth/LoginPage.vue'),
    meta: { title: 'Portal Auth TTE BSrE - BSSN', guestOnly: true }
  },
  {
    path: '/login/khususit',
    name: 'login-khusus-it',
    component: () => import('pages/auth/LoginKhususItPage.vue'),
    meta: { title: 'Login Khusus IT - E-DOC BSrE', guestOnly: true }
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('pages/DashboardPage.vue'),
        meta: { title: 'E-RM Dokumen & TTE BSRE', requiresAuth: true }
      }
    ]
  },
  {
    path: '/:catchAll(.*)*',
    redirect: '/'
  }
]

export default routes
