<template>
  <NavDrawer
    :title="viewingName ? `Study · ${viewingName}` : 'Study'"
    :viewing-name="viewingName"
    :viewing-user-id="viewingUserId"
  >
    <v-container fluid class="pa-6">
      <div class="d-flex flex-wrap align-center justify-space-between ga-3 mb-4">
        <div>
          <h1 class="text-h4">Study</h1>
          <p class="text-medium-emphasis mb-0">
            <span v-if="viewingName">Viewing {{ viewingName }}'s flashcards · </span>
            {{ studyCourseName }} · Card {{ studyIndex + 1 }} of {{ studyCards.length || 0 }}
          </p>
        </div>
        <v-select
          v-model="studyCourseId"
          :items="courses"
          item-title="name"
          item-value="id"
          label="Course"
          density="comfortable"
          hide-details
          style="max-width: 280px"
        />
      </div>

      <div v-if="currentCard" class="study-wrap mx-auto">
        <FlashCard
          study
          :front="currentCard.front"
          :back="currentCard.back"
          :flipped="flipped"
          @toggle="flipped = !flipped"
        />

        <div class="d-flex justify-center ga-3 mt-6">
          <v-btn
            prepend-icon="mdi-chevron-left"
            variant="tonal"
            :disabled="studyIndex <= 0"
            @click="prevCard"
          >
            Prev
          </v-btn>
          <v-btn
            prepend-icon="mdi-rotate-3d-variant"
            variant="outlined"
            @click="flipped = !flipped"
          >
            Flip
          </v-btn>
          <v-btn
            append-icon="mdi-chevron-right"
            color="primary"
            variant="flat"
            :disabled="studyIndex >= studyCards.length - 1"
            @click="nextCard"
          >
            Next
          </v-btn>
        </div>
      </div>

      <v-alert
        v-else
        type="warning"
        variant="tonal"
        text="This course has no flashcards. Open the course and add some first."
      />
    </v-container>
  </NavDrawer>
</template>

<script>
import NavDrawer from '@/components/NavDrawer.vue'
import FlashCard from '@/components/FlashCard.vue'
import api from '@/plugins/axios'

export default {
  name: 'StudyPage',
  components: { NavDrawer, FlashCard },
  data () {
    return {
      studyCourseId: '',
      studyIndex: 0,
      flipped: false,
      otherCourses: [],
      otherName: '',
    }
  },
  computed: {
    viewingUserId () {
      const id = this.$route.query.user
      if (!id || String(id) === String(this.$store.state.user?.id)) return ''
      return id
    },
    viewingName () {
      return this.viewingUserId ? this.otherName : ''
    },
    courses () {
      return this.viewingUserId ? this.otherCourses : this.$store.getters.courses
    },
    studyCards () {
      const found = this.courses.find((c) => String(c.id) === String(this.studyCourseId))
      return found ? found.cards.filter((card) => card.is_approved) : []
    },
    studyCourseName () {
      const found = this.courses.find((c) => String(c.id) === String(this.studyCourseId))
      return found ? found.name : 'Select a course'
    },
    currentCard () {
      return this.studyCards[this.studyIndex] || null
    },
  },
  watch: {
    studyCourseId () {
      this.studyIndex = 0
      this.flipped = false
      this.syncQuery()
    },
    '$route.query.course': {
      immediate: true,
      handler (value) {
        this.applyCourseQuery(value)
      },
    },
    courses () {
      this.applyCourseQuery(this.$route.query.course)
    },
    viewingUserId: {
      immediate: true,
      handler () {
        this.loadOtherCourses()
      },
    },
  },
  methods: {
    async loadOtherCourses () {
      if (!this.viewingUserId) {
        this.otherCourses = []
        this.otherName = ''
        return
      }
      const userId = this.viewingUserId
      const person = await api(`/api/users/${userId}`, {}, 'GET')
      this.otherName = person.name
      this.otherCourses = await api(
        `/api/courses?user_id=${userId}&viewer_id=${this.$store.state.user.id}`,
        {},
        'GET',
      )
      this.applyCourseQuery(this.$route.query.course)
    },
    applyCourseQuery (value) {
      const matches = (id) => this.courses.some((c) => String(c.id) === String(id))
      if (value && matches(value)) {
        this.studyCourseId = value
      } else if (this.courses.length && !matches(this.studyCourseId)) {
        this.studyCourseId = this.courses[0].id
      }
    },
    syncQuery () {
      if (this.studyCourseId && String(this.$route.query.course) !== String(this.studyCourseId)) {
        const query = { course: this.studyCourseId }
        if (this.viewingUserId) query.user = this.viewingUserId
        this.$router.replace({
          name: 'study',
          query,
        })
      }
    },
    nextCard () {
      if (this.studyIndex < this.studyCards.length - 1) {
        this.studyIndex += 1
        this.flipped = false
      }
    },
    prevCard () {
      if (this.studyIndex > 0) {
        this.studyIndex -= 1
        this.flipped = false
      }
    },
  },
}
</script>

<style scoped>
.study-wrap {
  max-width: 560px;
}
</style>
