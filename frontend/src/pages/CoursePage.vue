<template>
  <NavDrawer :title="course ? course.name : 'Course'">
    <v-container fluid class="pa-6">
      <div v-if="course">
        <div class="d-flex flex-wrap align-center justify-space-between ga-3 mb-4">
          <div>
            <h1 class="text-h4">{{ course.name }}</h1>
            <p class="text-medium-emphasis mb-0">
              {{ approvedCards.length }} flashcards
            </p>
          </div>
          <div class="d-flex ga-2">
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              variant="flat"
              @click="openAddCard"
            >
              Add flashcard
            </v-btn>
            <v-btn
              prepend-icon="mdi-play"
              variant="tonal"
              :disabled="!approvedCards.length"
              :to="{ name: 'study', query: { course: course.id } }"
            >
              Study
            </v-btn>
          </div>
        </div>

        <v-row v-if="approvedCards.length">
          <v-col
            v-for="card in approvedCards"
            :key="card.id"
            cols="12"
            sm="6"
            md="4"
          >
            <FlashCard
              can-delete
              :front="card.front"
              :back="card.back"
              :flipped="!!flippedIds[card.id]"
              @toggle="toggleFlip(card.id)"
              @delete="removeCard(card)"
            />
          </v-col>
        </v-row>

        <v-alert
          v-else
          type="info"
          variant="tonal"
          text="No flashcards yet. Add one to get started."
        />

        <div v-if="pendingCards.length" class="mt-8">
          <h2 class="text-h6 mb-1">Waiting for your approval</h2>
          <p class="text-medium-emphasis mb-4">
            A friend suggested these. They stay hidden until you approve them.
          </p>
          <v-row>
            <v-col
              v-for="card in pendingCards"
              :key="card.id"
              cols="12"
              sm="6"
              md="4"
            >
              <FlashCard
                can-delete
                :front="card.front"
                :back="card.back"
                :flipped="!!flippedIds[card.id]"
                @toggle="toggleFlip(card.id)"
                @delete="removeCard(card)"
              />
              <v-btn
                class="mt-2"
                block
                color="primary"
                variant="flat"
                prepend-icon="mdi-check"
                @click="approveCard(card)"
              >
                Approve
              </v-btn>
            </v-col>
          </v-row>
        </div>
      </div>

      <v-alert
        v-else
        type="error"
        variant="tonal"
        text="Course not found."
      />
    </v-container>

    <v-dialog v-model="cardDialog" max-width="520">
      <v-card>
        <v-card-title>Add flashcard</v-card-title>
        <v-card-text>
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
          <v-btn color="primary" variant="flat" @click="saveCard">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :timeout="2200" color="primary">
      {{ snackText }}
    </v-snackbar>
  </NavDrawer>
</template>

<script>
import NavDrawer from '@/components/NavDrawer.vue'
import FlashCard from '@/components/FlashCard.vue'

export default {
  name: 'CoursePage',
  components: { NavDrawer, FlashCard },
  props: {
    id: { type: String, required: true },
  },
  data () {
    return {
      flippedIds: {},
      cardDialog: false,
      newCardFront: '',
      newCardBack: '',
      snackbar: false,
      snackText: '',
    }
  },
  computed: {
    course () {
      return this.$store.getters.courseById(this.id)
    },
    approvedCards () {
      return (this.course?.cards || []).filter((card) => card.is_approved)
    },
    pendingCards () {
      return (this.course?.cards || []).filter((card) => !card.is_approved)
    },
  },
  watch: {
    id () {
      this.flippedIds = {}
    },
  },
  methods: {
    toggleFlip (cardId) {
      this.flippedIds = {
        ...this.flippedIds,
        [cardId]: !this.flippedIds[cardId],
      }
    },
    openAddCard () {
      this.newCardFront = ''
      this.newCardBack = ''
      this.cardDialog = true
    },
    async saveCard () {
      const front = this.newCardFront.trim()
      const back = this.newCardBack.trim()

      if (!front || !back) {
        this.snackText = 'Fill in both question and answer'
        this.snackbar = true
        return
      }

      await this.$store.dispatch('addCard', {
        courseId: this.id,
        front,
        back,
      })

      this.cardDialog = false
      this.newCardFront = ''
      this.newCardBack = ''
      this.snackText = 'Flashcard added'
      this.snackbar = true
    },
    async removeCard (card) {
      await this.$store.dispatch('deleteCard', { courseId: this.id, cardId: card.id })
      this.snackText = 'Flashcard removed'
      this.snackbar = true
    },
    async approveCard (card) {
      await this.$store.dispatch('approveCard', { courseId: this.id, cardId: card.id })
      this.snackText = 'Flashcard approved'
      this.snackbar = true
    },
  },
}
</script>
