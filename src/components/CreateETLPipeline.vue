<template>
  <div class="container">
    <h2>Create New ETL Pipeline</h2>
    <form @submit.prevent="submitPipeline">
      <!-- Pipeline Name Input -->
      <div class="form-group">
        <label for="pipelineName">Pipeline Name:</label>
        <input v-model="pipelineName" type="text" id="pipelineName" placeholder="Enter pipeline name" required />
      </div>

      <!-- Source Selection Dropdown -->
      <div class="form-group">
        <label for="source">Select Source:</label>
        <select v-model="selectedSource" id="source">
          <option v-for="source in sources" :key="source" :value="source">
            {{ source }}
          </option>
        </select>
      </div>

      <!-- Configuration Button -->
      <div class="form-group">
        <button type="button" @click="openConfiguration">Configuration</button>
      </div>

      <!-- Submit Button -->
      <div class="form-group">
        <button type="submit">Create Pipeline</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      pipelineName: "",
      selectedSource: "",
      sources: ["Database", "API", "CSV File", "JSON File"], // Példa források
    };
  },
  methods: {
    submitPipeline() {
      alert(`Pipeline Created:\nName: ${this.pipelineName}\nSource: ${this.selectedSource}`);
    },
    openConfiguration() {
      alert("Configuration settings will be implemented here!");
    },
  },
};
</script>

<style scoped>
.container {
  width: 50%;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #f9f9f9;
  text-align: center;
}

.form-group {
  margin-bottom: 15px;
}

input, select, button {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
