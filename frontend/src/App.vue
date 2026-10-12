<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
  //
</script>

<script>
export default {
  mounted () {
    if (this.$store.state.token) {
      this.$store.dispatch('fetchPlan')
    }
  },
}
</script>

<!-- import custom fonts -->
<style src="./styles/variables.scss"></style>
