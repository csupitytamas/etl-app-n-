<template>
  <div class="settings-container">
    <h2>Settings</h2>
    <!-- Téma mód -->
    <div class="form-group">
      <label> Thema:</label>
      <select v-model="theme">
        <option value="light"> Light mode</option>
        <option value="dark">Dark mode</option>
      </select>
    </div>

    <!-- Időzóna -->
    <div class="form-group">
      <label>🕐 Time zone:</label>
      <select v-model="timezone">
        <option value="Europe/Budapest">Budapest</option>
        <option value="UTC">UTC</option>
        <option value="America/New_York">New York</option>
        <option value="Asia/Tokyo">Tokyo</option>
      </select>
    </div>

    <!-- Mentési útvonal -->
    <div class="form-group">
      <label>💾 Default save path:</label>
      <input type="text" v-model="savePath" />
    </div>

    <div class="form-group">
      <button @click="saveSettings">Mentés</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "Settings",
  data() {
    return {
      language: "hu",
      theme: "light",
      timezone: "Europe/Budapest",
      savePath: ""
    };
  },
  methods: {
    saveSettings() {
      alert("✅ Beállítások mentve!");
      // Itt később lehet menteni fájlba, vagy IPC-n keresztül backendnek küldeni
    }
  }
};
</script>

<style scoped>
.settings-container {
  width: 60%;
  max-width: 700px;
  margin: 40px auto;
  padding: 25px;
  background: #f5f5f5;
  border-radius: 10px;
  border: 1px solid #ccc;
  font-family: "Segoe UI", sans-serif;
}

h2 {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
}

input,
select {
  padding: 8px;
  font-size: 14px;
  border-radius: 5px;
  border: 1px solid #bbb;
}

button {
  background-color: #007bff;
  color: white;
  padding: 10px;
  font-size: 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
