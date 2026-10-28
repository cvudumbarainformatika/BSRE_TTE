import { boot } from 'quasar/wrappers'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

/*
 * If not building with SSR mode, you can
 * directly export the Pinia instantiation;
 */

export default boot(({ app }) => {
  const pinia = createPinia()
  pinia.use(piniaPluginPersistedstate)

  app.use(pinia)
})