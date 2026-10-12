/**
 * plugins/index.ts
 *
 * Automatically included in `./src/main.ts`
 */

// Types
import type { App } from 'vue'

// Plugins
import ToastPlugin from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import vuetify from './vuetify'
import router from '../../router'
import store from '@/store'

export function registerPlugins (app: App) {
  app.use(vuetify)
  app.use(router)
  app.use(store)
  app.use(ToastPlugin)
}
