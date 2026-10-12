<template>
  <div>
    <v-app-bar flat>
      <v-app-bar-nav-icon class="d-lg-none" @click="drawer = !drawer" />
      <v-app-bar-title>{{ title }}</v-app-bar-title>
      <template #append>
        <slot name="actions" />
        <SocialBar />
        <v-btn icon="mdi-theme-light-dark" @click="$vuetify.theme.cycle()" />
      </template>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      :rail="rail && !mobile"
      expand-on-hover
      permanent
    >
      <v-list-item
        class="py-4"
        prepend-icon="mdi-cards-outline"
        :subtitle="rail && !mobile ? undefined : drawerSubtitle"
        title="FlashDeck"
      />

      <v-divider />

      <v-list v-if="viewingName" density="compact" nav>
        <v-list-item
          prepend-icon="mdi-play-circle-outline"
          title="Study"
          :to="studyLink"
          :active="isStudy"
        />
      </v-list>

      <template v-else>
        <v-list density="compact" nav>
          <v-list-item
            prepend-icon="mdi-home-outline"
            title="Home"
            :to="{ name: 'home' }"
            :active="isHome"
          />
          <v-list-item
            prepend-icon="mdi-play-circle-outline"
            title="Study"
            :to="{ name: 'study' }"
            :active="isStudy"
          />
        </v-list>

        <v-divider class="my-2" />

        <v-list-subheader>Courses</v-list-subheader>

        <v-list density="compact" nav>
          <v-list-item
            v-for="course in courses"
            :key="course.id"
            :prepend-icon="course.icon"
            :title="course.name"
            :subtitle="rail && !mobile ? undefined : `${approvedCount(course)} cards`"
            :to="{ name: 'course', params: { id: course.id } }"
            :active="isCourse(course.id)"
          />
        </v-list>
      </template>

      <template #append>
        <div class="pa-2">
          <v-list-item
            v-if="userName && !(rail && !mobile)"
            class="px-0 mb-2"
            :title="userName"
            :subtitle="userEmail"
            prepend-icon="mdi-account-circle-outline"
          />
          <v-btn
            v-if="viewingName"
            block
            prepend-icon="mdi-arrow-left"
            variant="tonal"
            :to="{ name: 'home' }"
          >
            <span v-if="!(rail && !mobile)">My flashcards</span>
          </v-btn>
          <v-btn
            v-else
            block
            color="primary"
            prepend-icon="mdi-plus"
            variant="tonal"
            @click="courseDialog = true"
          >
            Add course
          </v-btn>
          <v-btn
            class="mt-2"
            block
            prepend-icon="mdi-logout"
            variant="text"
            @click="logout"
          >
            <span v-if="!(rail && !mobile)">Logout</span>
          </v-btn>
          <v-btn
            class="mt-2"
            block
            :icon="rail && !mobile ? 'mdi-chevron-right' : undefined"
            :prepend-icon="rail && !mobile ? undefined : 'mdi-chevron-left'"
            variant="text"
            @click="rail = !rail"
          >
            <span v-if="!(rail && !mobile)">Collapse</span>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <slot />

    <v-dialog v-model="courseDialog" max-width="480">
      <v-card>
        <v-card-title>Add course</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newCourseName"
            label="Course name"
            autofocus
            @keyup.enter="saveCourse"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="courseDialog = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveCourse">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { useDisplay } from 'vuetify'
import SocialBar from '@/components/SocialBar.vue'

export default {
  name: 'NavDrawer',
  components: { SocialBar },
  props: {
    title: {
      type: String,
      default: '',
    },
    viewingName: {
      type: String,
      default: '',
    },
    viewingUserId: {
      type: [String, Number],
      default: '',
    },
  },
  setup () {
    const { mobile } = useDisplay()
    return { mobile }
  },
  data () {
    return {
      drawer: true,
      rail: false,
      courseDialog: false,
      newCourseName: '',
    }
  },
  computed: {
    courses () {
      return this.$store.getters.courses
    },
    isHome () {
      return this.$route.name === 'home'
    },
    isStudy () {
      return this.$route.name === 'study'
    },
    userName () {
      return this.$store.state.user?.name || ''
    },
    userEmail () {
      return this.$store.state.user?.email || ''
    },
    drawerSubtitle () {
      if (this.viewingName) return `Viewing ${this.viewingName}'s flashcards`
      return 'Course flashcards'
    },
    studyLink () {
      return { name: 'study', query: { user: this.viewingUserId } }
    },
  },
  mounted () {
    this.$store.dispatch('fetchCourses')
  },
  methods: {
    approvedCount (course) {
      return (course.cards || []).filter((card) => card.is_approved).length
    },
    isCourse (id) {
      return this.$route.name === 'course' && String(this.$route.params.id) === String(id)
    },
    async saveCourse () {
      const name = this.newCourseName.trim()
      if (!name) return

      const course = await this.$store.dispatch('addCourse', name)
      this.newCourseName = ''
      this.courseDialog = false
      this.$router.push({ name: 'course', params: { id: course.id } })
    },
    logout () {
      this.$store.commit('resetState')
      this.$router.push({ name: 'login' })
    },
  },
}
</script>
