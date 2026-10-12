import axios from 'axios'
import Store from '@/store'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

const $toast = useToast()

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const APP_DEBUG = import.meta.env.VITE_APP_DEBUG === 'true'

/**
 * Shared AJAX helper for FlashDeck pages.
 *
 * Usage:
 *   import api from '@/plugins/axios'
 *   const data = await api('/api/users', {}, 'GET')
 *   const user = await api('/api/users/register', { name, email, password }, 'POST')
 */
export default async (
  url,
  payload = {},
  method = 'GET',
  params = {},
  customErrResponse = null
) => {
  const token = Store.state.token
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const fullUrl = `${API_URL}${url.startsWith('/') ? url : `/${url}`}`

  try {
    if (APP_DEBUG) {
      console.log('Request URL:', fullUrl)
      console.log('Method:', method)
      console.log('Payload:', payload)
      console.log('Params:', params)
    }

    const requestParams = method.toUpperCase() === 'GET' ? payload : params

    const response = await axios({
      headers,
      method,
      url: fullUrl,
      params: requestParams,
      data: method.toUpperCase() === 'GET' ? undefined : payload,
      timeout: 30000,
    })

    if (APP_DEBUG) {
      console.log('Response:', response.data)
    }

    return response.data
  } catch (error) {
    const status = error.response?.status
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Request failed'

    if (APP_DEBUG) {
      console.error('API Error:', error.response || error)
    }

    if (customErrResponse) {
      customErrResponse(error.response?.data || { message })
    } else {
      $toast.error(typeof message === 'string' ? message : JSON.stringify(message), {
        duration: 3000,
        position: 'top-right',
      })
    }

    if (status === 401) {
      Store.commit('resetState')
      if (window.location.pathname !== '/') {
        window.location.href = '/'
      }
    }

    throw error
  }
}
