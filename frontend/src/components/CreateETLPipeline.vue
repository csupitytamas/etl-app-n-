<template>
  <div class="container">
    <h2>Create New ETL Pipeline</h2>
    <form @submit.prevent="submitPipeline" class="form-layout">
      <!-- Pipeline Name Input -->
      <div class="form-row">
        <label for="pipelineName">Pipeline Name:</label>
        <input v-model="pipelineName" type="text" id="pipelineName" placeholder="Enter pipeline name" required />
      </div>

      <!-- Source Selection Dropdown -->
      <div class="form-row">
        <label for="source">Select Source:</label>
        <select v-model="selectedSource" id="source">
          <option disabled value="">Please select</option>
          <option v-for="source in sources" :key="source" :value="source">
            {{ source }}
          </option>
        </select>
      </div>

      <!-- Buttons -->
      <div class="button-row">
        <button type="button" class="secondary" @click="openConfiguration">Configuration</button>
        <button type="submit" class="primary">Create Pipeline</button>
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
      sources: ["Database", "API", "CSV File", "JSON File"],
    };
  },
  methods: {
    submitPipeline() {
      alert(`Pipeline Created:\nName: ${this.pipelineName}\nSource: ${this.selectedSource}`);
    },
    openConfiguration() {
      this.$router.push("/etl-config");
    },
  },
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: 40px auto;
  padding: 30px;
  background: #f5f7fa;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-family: 'Segoe UI', sans-serif;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-weight: 600;
  font-size: 15px;
  text-align: left;
}

input, select {
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
}

select {
  text-align: center;
  width: 100%;
  min-width: 160px;
}



.button-row {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

button {
  flex: 1;
  padding: 10px;
  font-size: 15px;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  transition: 0.2s ease-in-out;
}

button.primary {
  background-color: #007bff;
  color: white;
}

button.primary:hover {
  background-color: #0056b3;
}

button.secondary {
  background-color: #e0e0e0;
  color: #333;
}

button.secondary:hover {
  background-color: #c9c9c9;
}
</style>
