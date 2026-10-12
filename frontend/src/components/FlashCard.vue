<template>
  <div class="flash-shell">
    <v-btn
      v-if="canDelete"
      class="trash-btn"
      icon="mdi-delete-outline"
      size="small"
      variant="text"
      aria-label="Delete flashcard"
      @click.stop="$emit('delete')"
    />
  <div
    class="flip-card"
    :class="{ flipped: flipped, study: study }"
    @click="$emit('toggle')"
  >
    <div class="flip-inner">
      <v-card class="flip-face" rounded="lg" variant="elevated">
        <v-card-text class="d-flex flex-column fill-height justify-center text-center" :class="study ? 'pa-8' : ''">
          <div class="text-caption text-medium-emphasis mb-2">Question</div>
          <div :class="study ? 'text-h5' : 'text-body-1 font-weight-medium'">
            {{ front }}
          </div>
          <div class="text-caption text-medium-emphasis mt-4">
            {{ study ? 'Click card to reveal answer' : 'Click to flip' }}
          </div>
        </v-card-text>
      </v-card>

      <v-card class="flip-face flip-back" color="primary" rounded="lg" variant="flat">
        <v-card-text class="d-flex flex-column fill-height justify-center text-center" :class="study ? 'pa-8' : ''">
          <div class="text-caption mb-2 opacity-80">Answer</div>
          <div :class="study ? 'text-h5' : 'text-body-1 font-weight-medium'">
            {{ back }}
          </div>
          <div class="text-caption mt-4 opacity-80">
            {{ study ? 'Click to hide answer' : 'Click to flip back' }}
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
  </div>
</template>

<script>
export default {
  name: 'FlashCard',
  props: {
    front: { type: String, required: true },
    back: { type: String, required: true },
    flipped: { type: Boolean, default: false },
    study: { type: Boolean, default: false },
    canDelete: { type: Boolean, default: false },
  },
  emits: ['toggle', 'delete'],
}
</script>

<style scoped>
.flash-shell {
  position: relative;
}

.trash-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 2;
}

.flip-card {
  height: 200px;
  perspective: 1000px;
  cursor: pointer;
}

.flip-card.study {
  height: 280px;
}

.flip-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.55s ease;
  transform-style: preserve-3d;
}

.flip-card.flipped .flip-inner {
  transform: rotateY(180deg);
}

.flip-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  display: flex;
}

.flip-face :deep(.v-card-text) {
  width: 100%;
}

.flip-back {
  transform: rotateY(180deg);
}
</style>
