<template>
  <div class="config-container">
    <h2>Register</h2>

    <div class="form-group">
      <label>Email</label>
      <input type="email" v-model="email" placeholder="Email" />
    </div>

    <div class="form-group">
      <label>Password</label>
      <input type="password" v-model="password" placeholder="Password" />
    </div>

    <div class="form-group">
      <label>Confirm Password</label>
      <input type="password" v-model="confirmPassword" placeholder="Repeat Password" />
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <button @click="register">Register</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser } from '@/api/user.js'
const router = useRouter()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')

const register = async () => {
  error.value = ''
  if (password.value !== confirmPassword.value) {
    error.value = 'A jelszavak nem egyeznek!'
    return
  }

  try {
    await registerUser(email.value, password.value)
    alert('Sikeres regisztráció!')
    // opcionálisan redirect pl.: router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Hiba történt a regisztráció során.'
  }
}
</script>

<style scoped>
.config-container {
  max-width: 400px;
  margin: auto;
}

.form-group {
  margin-bottom: 1rem;
}

input {
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