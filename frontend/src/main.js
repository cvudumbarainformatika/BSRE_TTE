import { createApp } from 'vue'
import { Quasar } from 'quasar'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth' // Import store auth

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css'

// Import Quasar css
import 'quasar/src/css/index.sass'

// Assumes your root component is App.vue
// and placed in same folder as main.js
import App from './App.vue'
import router from './router'

// Import Tailwind CSS
import './css/tailwind.css'
import './css/app.scss'

// Import test function
import { testLogin } from './test-login'

const myApp = createApp(App)

myApp.use(Quasar, {
  plugins: {}, // import Quasar plugins and add here
})

const pinia = createPinia()
myApp.use(pinia)
myApp.use(router)

// Muat data auth dari storage saat aplikasi dimulai
const authStore = useAuthStore()
authStore.checkAuthStatus()

// Assumes you have a <div id="app"></div> in your index.html
myApp.mount('#app')

// Attach testLogin function to window object for easy access from browser console
window.testLogin = testLogin