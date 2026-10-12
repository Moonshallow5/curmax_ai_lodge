<template>
  <div class="d-flex align-center">
    <v-btn
      variant="text"
      prepend-icon="mdi-account-group-outline"
      @click="peopleDialog = true"
    >
      People
    </v-btn>
    <v-menu location="bottom end">
      <template #activator="{ props }">
        <v-btn v-bind="props" icon>
          <v-badge
            color="error"
            :content="incomingRequests.length"
            :model-value="incomingRequests.length > 0"
          >
            <v-icon>mdi-bell-outline</v-icon>
          </v-badge>
        </v-btn>
      </template>
      <v-card min-width="320">
        <v-card-title class="text-subtitle-1">Friend requests</v-card-title>
        <v-list v-if="incomingRequests.length">
          <v-list-item
            v-for="request in incomingRequests"
            :key="request.id"
            :title="request.requester.name"
            subtitle="Sent you a friend request"
          >
            <template #append>
              <v-btn size="small" color="primary" variant="flat" class="mr-1" @click="acceptRequest(request)">
                Accept
              </v-btn>
              <v-btn size="small" variant="text" @click="declineRequest(request)">
                Decline
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
        <v-card-text v-else class="text-medium-emphasis">
          No friend requests
        </v-card-text>
      </v-card>
    </v-menu>

    <v-dialog v-model="peopleDialog" max-width="520">
      <v-card>
        <v-card-title>People</v-card-title>
        <v-card-text>
          <p class="text-medium-emphasis mb-4">
            Open someone else's profile to read their flashcards.
          </p>
          <v-list v-if="otherUsers.length" border rounded="lg">
            <v-list-item
              v-for="person in otherUsers"
              :key="person.id"
              :title="person.name"
              :subtitle="person.email"
            >
              <template #append>
                <v-btn
                  size="small"
                  variant="tonal"
                  class="mr-1"
                  @click="openProfile(person)"
                >
                  Flashcards
                </v-btn>
                <v-btn
                  v-if="friendState(person.id) === 'none'"
                  size="small"
                  color="primary"
                  variant="flat"
                  @click="sendRequest(person)"
                >
                  Add friend
                </v-btn>
                <v-chip v-else-if="friendState(person.id) === 'sent'" size="small">
                  Requested
                </v-chip>
                <v-chip v-else-if="friendState(person.id) === 'incoming'" size="small" color="primary">
                  Respond
                </v-chip>
                <v-chip v-else size="small" color="success">
                  Friends
                </v-chip>
              </template>
            </v-list-item>
          </v-list>
          <v-alert
            v-else
            type="info"
            variant="tonal"
            text="No other people yet. Register another account to visit their flashcards."
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="peopleDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import api from '@/plugins/axios'

export default {
  name: 'SocialBar',
  data () {
    return {
      users: [],
      requests: [],
      peopleDialog: false,
    }
  },
  computed: {
    me () {
      return this.$store.state.user
    },
    otherUsers () {
      if (!this.me) return this.users
      return this.users.filter((user) => user.id !== this.me.id)
    },
    incomingRequests () {
      if (!this.me) return []
      return this.requests.filter((request) =>
        request.status === 'pending' && request.addressee_id === this.me.id
      )
    },
  },
  mounted () {
    this.loadUsers()
    this.loadRequests()
  },
  methods: {
    async loadUsers () {
      try {
        this.users = await api('/api/users', {}, 'GET')
      } catch (error) {
        this.users = []
      }
    },
    async loadRequests () {
      if (!this.me) return
      try {
        this.requests = await api(`/api/friend-requests?user_id=${this.me.id}`, {}, 'GET')
      } catch (error) {
        this.requests = []
      }
    },
    friendState (userId) {
      const row = this.requests.find((request) =>
        request.requester_id === userId || request.addressee_id === userId
      )
      if (!row || row.status === 'declined') return 'none'
      if (row.status === 'accepted') return 'friends'
      if (row.requester_id === this.me.id) return 'sent'
      return 'incoming'
    },
    openProfile (person) {
      this.peopleDialog = false
      this.$router.push({ name: 'profile', params: { id: person.id } })
    },
    async sendRequest (person) {
      await api('/api/friend-requests', {
        requester_id: this.me.id,
        addressee_id: person.id,
      }, 'POST')
      await this.loadRequests()
    },
    async acceptRequest (request) {
      await api(`/api/friend-requests/${request.id}/accept`, {}, 'POST')
      await this.loadRequests()
    },
    async declineRequest (request) {
      await api(`/api/friend-requests/${request.id}/decline`, {}, 'POST')
      await this.loadRequests()
    },
  },
}
</script>
