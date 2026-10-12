import { createStore } from 'vuex'
import api from '@/plugins/axios'

const initialState = () => ({
  token: null,
  user: null,
  plan: null,
  courses: [],
})

export default createStore({
  state: initialState(),
  getters: {
    courses: (state) => state.courses,
    courseById: (state) => (id) =>
      state.courses.find((c) => String(c.id) === String(id)) || null,
  },
  mutations: {
    SET_TOKEN (state, token) {
      state.token = token
    },
    SET_USER (state, user) {
      state.user = user
    },
    SET_PLAN (state, plan) {
      state.plan = plan
    },
    SET_COURSES (state, courses) {
      state.courses = courses
    },
    ADD_COURSE (state, course) {
      state.courses.push(course)
    },
    ADD_CARD (state, { courseId, card }) {
      const course = state.courses.find((c) => String(c.id) === String(courseId))
      if (course) {
        course.cards.push(card)
      }
    },
    REMOVE_CARD (state, { courseId, cardId }) {
      const course = state.courses.find((c) => String(c.id) === String(courseId))
      if (course) {
        course.cards = course.cards.filter((card) => card.id !== cardId)
      }
    },
    APPROVE_CARD (state, { courseId, cardId }) {
      const course = state.courses.find((c) => String(c.id) === String(courseId))
      const card = course && course.cards.find((item) => item.id === cardId)
      if (card) {
        card.is_approved = true
      }
    },
    resetState (state) {
      Object.assign(state, initialState())
    },
    clearLoading () {
      // placeholder for future loading flags used by axios helper
    },
  },
  actions: {
    fetchPlan ({ commit, state }) {
      if (!state.token) return
      commit('SET_PLAN', { name: 'default' })
    },
    async fetchCourses ({ commit, state }) {
      if (!state.user) return []
      const courses = await api(`/api/courses?user_id=${state.user.id}&viewer_id=${state.user.id}`, {}, 'GET')
      commit('SET_COURSES', courses)
      return courses
    },
    async addCourse ({ commit, state }, name) {
      const course = await api('/api/courses', {
        name,
        user_id: state.user.id,
        icon: 'mdi-book-open-page-variant-outline',
      }, 'POST')
      commit('ADD_COURSE', { ...course, cards: course.cards || [] })
      return course
    },
    async addCard ({ commit, state }, { courseId, front, back }) {
      const card = await api('/api/flashcards', {
        front,
        back,
        course_id: Number(courseId),
        user_id: state.user.id,
      }, 'POST')
      commit('ADD_CARD', { courseId, card })
      return card
    },
    async deleteCard ({ commit, state }, { courseId, cardId }) {
      await api(`/api/flashcards/${cardId}/delete?user_id=${state.user.id}`, {}, 'POST')
      commit('REMOVE_CARD', { courseId, cardId })
    },
    async approveCard ({ commit, state }, { courseId, cardId }) {
      await api(`/api/flashcards/${cardId}/approve?user_id=${state.user.id}`, {}, 'POST')
      commit('APPROVE_CARD', { courseId, cardId })
    },
  },
})
