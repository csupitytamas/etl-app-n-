<template>
  <div class="history-container">
    <h2>All Process</h2>
    <ul class="etl-list">
      <li v-for="pipeline in pipelines" :key="pipeline.id" class="etl-item">
        {{ pipeline.name }} - {{ pipeline.created }}
        <button class="log-btn" @click="viewLog(pipeline)">
          📄 View Log
        </button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: "History",
  data() {
    return {
      pipelines: [
        { id: 1, name: "My pipeline", created: "2025-03-29 15:22" },
        { id: 2, name: "Your pipeline", created: "2025-03-28 10:11" },
        { id: 3, name: "Our pipeline", created: "2025-03-27 08:40" }
      ]
    };
  },
  methods: {
    viewLog(pipeline) {
      alert(`📋 Log megnyitása: ${pipeline.name}\n\n(Itt nyílik majd meg a log fájl tartalma)`);
    }
  }
};
</script>

<style scoped>
.history-container {
  width: 60%;
  margin: 30px auto;
  padding: 20px;
  border: 1px solid #ccc;
  background-color: #fefefe;
  border-radius: 8px;
}

.etl-list {
  list-style-type: none;
  padding: 0;
}

.etl-list li {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  font-size: 16px;
}

.log-btn {
  float: right;
}
</style>