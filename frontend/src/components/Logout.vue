<template>
  <div class="logout-container">
    <p>Kijelentkezés folyamatban...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { logoutUser } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')

  if (token) {
    try {
      await logoutUser(token)
    } catch (err) {
      console.warn('Kijelentkezés nem sikerült a backend felől:', err)
    }
    localStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_token')
    localStorage.removeItem('user_id')
    sessionStorage.removeItem('user_id')
  }

  userStore.user = null
  router.push('/login')
})
</script>

<style scoped>
.logout-container {
  text-align: center;
  padding: 2rem;
}
</style>