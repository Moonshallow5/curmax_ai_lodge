<template>
  <div class="login-container">
    <v-row class="login-row" no-gutters>
      <v-col cols="12" md="4" class="brand-panel d-none d-md-flex">
        <div class="brand-content">
          <v-icon icon="mdi-cards-outline" size="64" class="mb-4" />
          <h2 class="text-h4 font-weight-bold mb-2">FlashDeck</h2>
          <p class="text-body-1 opacity-90">
            Create an account to save your study progress.
          </p>
        </div>
      </v-col>

      <v-col cols="12" md="8" class="form-panel">
        <v-form class="login-form" @submit.prevent="register">
          <h3 class="text-h5 text-center mb-8 form-title">
            Create your account
          </h3>

          <p class="text-body-1 text-format mb-1">Name</p>
          <v-text-field
            v-model="name"
            class="mb-5"
            label="Enter your name"
            variant="outlined"
            density="comfortable"
          />

          <p class="text-body-1 text-format mb-1">Email</p>
          <v-text-field
            v-model="email"
            class="mb-5"
            label="Enter your email here"
            hint="eg. johndoe@gmail.com"
            persistent-hint
            type="email"
            autocomplete="email"
            variant="outlined"
            density="comfortable"
          />

          <p class="text-body-1 text-format mb-1">Password</p>
          <v-text-field
            v-model="password"
            class="mb-5"
            label="Enter your password here"
            hint="minimum 6 characters"
            persistent-hint
            type="password"
            autocomplete="new-password"
            variant="outlined"
            density="comfortable"
            @keyup.enter="register"
          />

          <v-btn
            block
            color="primary"
            class="mt-1"
            style="text-transform: none; font-size: 15px"
            :disabled="!canRegister"
            :loading="loading"
            @click="register"
          >
            Register
          </v-btn>

          <div class="d-flex justify-center mt-4 text-body-2">
            Already have an account?
            <span class="register-link ml-1" @click="goLogin">
              Login
            </span>
          </div>
        </v-form>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import api from '@/plugins/axios'

export default {
  name: 'RegisterPage',
  data () {
    return {
      name: '',
      email: '',
      password: '',
      loading: false,
    }
  },
  computed: {
    canRegister () {
      return (
        this.name.trim().length > 0 &&
        this.email.trim().includes('@') &&
        this.password.length >= 6
      )
    },
  },
  methods: {
    async register () {
      if (!this.canRegister || this.loading) return

      this.loading = true
      try {
        const user = await api(
          '/api/users/register',
          {
            name: this.name.trim(),
            email: this.email.trim(),
            password: this.password,
          },
          'POST'
        )

        this.$store.commit('SET_USER', user)
        this.$store.commit('SET_TOKEN', `user-${user.id}`)
        this.$router.push({ name: 'home' })
      } catch (error) {
        // toast handled in axios helper
      } finally {
        this.loading = false
      }
    },
    goLogin () {
      this.$router.push({ name: 'login' })
    },
  },
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: #f7f7f8;
}

.login-row {
  min-height: 100vh;
}

.brand-panel {
  align-items: center;
  justify-content: center;
  background:
    linear-gradient(160deg, rgba(25, 118, 210, 0.92), rgba(13, 71, 161, 0.95)),
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.18), transparent 45%);
  color: white;
  padding: 2rem;
}

.brand-content {
  max-width: 280px;
  text-align: center;
}

.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  background: #fff;
}

.login-form {
  width: 100%;
  max-width: 420px;
}

.form-title {
  color: rgb(var(--v-theme-primary));
}

.text-format {
  font-weight: 500;
}

.register-link {
  color: rgb(var(--v-theme-primary));
  cursor: pointer;
  font-weight: 600;
}

.register-link:hover {
  text-decoration: underline;
}
</style>
