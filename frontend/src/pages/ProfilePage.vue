<template>
  <NavDrawer
    :title="profile ? profile.name : 'Profile'"
    :viewing-name="profile ? profile.name : ''"
    :viewing-user-id="id"
  >
    <template #actions>
      <v-btn
        v-if="friendState === 'none'"
        color="primary"
        variant="flat"
        prepend-icon="mdi-account-plus-outline"
        @click="sendRequest"
      >
        Add friend
      </v-btn>
      <v-chip v-else-if="friendState === 'sent'" class="mr-2">Requested</v-chip>
      <v-chip v-else-if="friendState === 'incoming'" class="mr-2" color="primary">
        Check the bell
      </v-chip>
      <v-chip v-else-if="friendState === 'friends'" class="mr-2" color="success">Friends</v-chip>
    </template>

    <v-container fluid class="pa-6">
      <div v-if="profile">
        <v-alert class="mb-4" type="info" variant="tonal">
          Viewing {{ profile.name }}'s flashcards
        </v-alert>
        <h1 class="text-h4 mb-1">{{ profile.name }}</h1>
        <p class="text-medium-emphasis mb-6">{{ profile.email }}</p>

        <div v-for="course in courses" :key="course.id" class="mb-8">
          <div class="d-flex flex-wrap align-center justify-space-between ga-2 mb-3">
            <h2 class="text-h6 mb-0">
              <v-icon :icon="course.icon" class="mr-2" />
              {{ course.name }}
            </h2>
            <div class="d-flex ga-2">
              <v-btn
                size="small"
                prepend-icon="mdi-play"
                variant="flat"
                color="primary"
                :disabled="!course.cards.length"
                :to="{ name: 'study', query: { user: id, course: course.id } }"
              >
                Study
              </v-btn>
              <v-btn
                v-if="friendState === 'friends'"
                size="small"
                variant="tonal"
                prepend-icon="mdi-plus"
                @click="openAddCard(course)"
              >
                Add flashcard
              </v-btn>
            </div>
          </div>
          <v-row v-if="course.cards.length">
            <v-col
              v-for="card in course.cards"
              :key="card.id"
              cols="12"
              sm="6"
              md="4"
            >
              <FlashCard
                :front="card.front"
                :back="card.back"
                :flipped="!!flippedIds[card.id]"
                @toggle="toggleFlip(card.id)"
              />
            </v-col>
          </v-row>
          <v-alert
            v-else
            type="info"
            variant="tonal"
            text="No flashcards in this course."
          />
        </div>

        <v-alert
          v-if="!courses.length"
          type="info"
          variant="tonal"
          text="This person has no courses yet."
        />
      </div>
    </v-container>

    <v-dialog v-model="cardDialog" max-width="520">
      <v-card>
        <v-card-title>Suggest a flashcard</v-card-title>
        <v-card-text>
          <p class="text-medium-emphasis mb-4">
            {{ profile ? profile.name : 'They' }} will need to approve this before it shows up.
          </p>
          <v-textarea
            v-model="newCardFront"
            label="Question (front)"
            rows="2"
            auto-grow
            class="mb-2"
          />
          <v-textarea
            v-model="newCardBack"
            label="Answer (back)"
            rows="2"
            auto-grow
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="cardDialog = false">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveCard">Send</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :timeout="2400" color="primary">
      {{ snackText }}
    </v-snackbar>
  </NavDrawer>
</template>

<script>
import FlashCard from '@/components/FlashCard.vue'
import NavDrawer from '@/components/NavDrawer.vue'
import api from '@/plugins/axios'

export default {
  name: 'ProfilePage',
  components: { FlashCard, NavDrawer },
  props: {
    id: {
      type: [String, Number],
      required: true,
    },
  },
  data () {
    return {
      profile: null,
      courses: [],
      requests: [],
      flippedIds: {},
      cardDialog: false,
      targetCourse: null,
      newCardFront: '',
      newCardBack: '',
      snackbar: false,
      snackText: '',
    }
  },
  computed: {
    me () {
      return this.$store.state.user
    },
    friendState () {
      const userId = Number(this.id)
      const row = this.requests.find((request) =>
        request.requester_id === userId || request.addressee_id === userId
      )
      if (!row || row.status === 'declined') return 'none'
      if (row.status === 'accepted') return 'friends'
      if (row.requester_id === this.me.id) return 'sent'
      return 'incoming'
    },
  },
  watch: {
    id () {
      this.flippedIds = {}
      this.load()
    },
  },
  mounted () {
    this.load()
  },
  methods: {
    async load () {
      const userId = Number(this.id)
      this.profile = await api(`/api/users/${userId}`, {}, 'GET')
      this.courses = await api(`/api/courses?user_id=${userId}&viewer_id=${this.me.id}`, {}, 'GET')
      this.requests = await api(`/api/friend-requests?user_id=${this.me.id}`, {}, 'GET')
    },
    toggleFlip (cardId) {
      this.flippedIds = {
        ...this.flippedIds,
        [cardId]: !this.flippedIds[cardId],
      }
    },
    openAddCard (course) {
      this.targetCourse = course
      this.newCardFront = ''
      this.newCardBack = ''
      this.cardDialog = true
    },
    async saveCard () {
      const front = this.newCardFront.trim()
      const back = this.newCardBack.trim()
      if (!front || !back || !this.targetCourse) return

      await api('/api/flashcards', {
        front,
        back,
        course_id: this.targetCourse.id,
        user_id: this.me.id,
      }, 'POST')

      this.cardDialog = false
      this.snackText = 'Sent for approval'
      this.snackbar = true
    },
    async sendRequest () {
      await api('/api/friend-requests', {
        requester_id: this.me.id,
        addressee_id: Number(this.id),
      }, 'POST')
      this.requests = await api(`/api/friend-requests?user_id=${this.me.id}`, {}, 'GET')
    },
  },
}
</script>
