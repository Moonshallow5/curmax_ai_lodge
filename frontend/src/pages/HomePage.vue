<template>
  <NavDrawer title="Home">
    <v-container fluid class="pa-6">
      <h1 class="text-h4 mb-2">FlashDeck</h1>
      <p class="text-medium-emphasis mb-6">
        Pick a course to add or review flashcards.
      </p>

      <v-row>
        <v-col
          v-for="course in courses"
          :key="course.id"
          cols="12"
          sm="6"
          md="4"
        >
          <v-card
            rounded="lg"
            variant="tonal"
            hover
            :to="{ name: 'course', params: { id: course.id } }"
          >
            <v-card-item>
              <template #prepend>
                <v-avatar :icon="course.icon" variant="tonal" />
              </template>
              <v-card-title>{{ course.name }}</v-card-title>
              <v-card-subtitle>{{ approvedCount(course) }} flashcards</v-card-subtitle>
            </v-card-item>
          </v-card>
        </v-col>
      </v-row>

      <v-alert
        v-if="!courses.length"
        class="mt-4"
        type="info"
        variant="tonal"
        text="No courses yet. Click Add course in the drawer."
      />
    </v-container>
  </NavDrawer>
</template>

<script>
import NavDrawer from '@/components/NavDrawer.vue'

export default {
  name: 'HomePage',
  components: { NavDrawer },
  computed: {
    courses () {
      return this.$store.getters.courses
    },
  },
  methods: {
    approvedCount (course) {
      return (course.cards || []).filter((card) => card.is_approved).length
    },
  },
}
</script>
