<template>
  <div class="config-container">
    <h2>Login</h2>

    <div class="form-group">
      <label>Email</label>
      <input type="email" v-model="email" placeholder="Email" />
    </div>

    <div class="form-group">
      <label>Password</label>
      <input type="password" v-model="password" placeholder="Password" />
    </div>

    <div class="form-group">
      <input type="checkbox" v-model="stayLoggedIn" id="stay" />
      <label for="stay">Maradjak bejelentkezve</label>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <button @click="login">Bejelentkezés</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser } from '@/api/user.js'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const email = ref('')
const password = ref('')
const stayLoggedIn = ref(false)
const error = ref('')
const userStore = useUserStore()

const login = async () => {
  error.value = ''

  try {
    const response = await loginUser(email.value, password.value, stayLoggedIn.value)
    const { token, user_id } = response.data

    // Tárolás a választás szerint
    if (stayLoggedIn.value) {
      localStorage.setItem('auth_token', token)
      localStorage.setItem('user_id', user_id)
    } else {
      sessionStorage.setItem('auth_token', token)
      sessionStorage.setItem('user_id', user_id)
    }

    alert('Sikeres bejelentkezés!')
    await userStore.loadUser()
    router.push('/')

  } catch (err) {
    error.value = err.response?.data?.detail || 'Hiba a bejelentkezés során.'
  }
}
</script>
cd
<style scoped>
.config-container {
  max-width: 400px;
  margin: auto;
}

.form-group {
  margin-bottom: 1rem;
}

input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
}

button {
  padding: 10px 20px;
  cursor: pointer;
}

.error-message {
  color: red;
  margin-bottom: 10px;
}
</style>