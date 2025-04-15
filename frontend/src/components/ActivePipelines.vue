<template>
  <div class="container">
    <h2>Active ETL Pipelines</h2>

    <table>
      <thead>
      <tr>
        <th>Name</th>
        <th>Source</th>
        <th>Config</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(pipeline, index) in pipelines" :key="index">
        <td>{{ pipeline.name }}</td>
        <td>{{ pipeline.source }}</td>
        <td>
          <button @click="configurePipeline(pipeline)">
            ⚙️
          </button>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: "ActivePipelines",
  data() {
    return {
      pipelines: [
        { name: "My pipeline", source: "API1"},
        { name: "Your pipeline", source: "API2 + userfile"},
        { name: "Our pipeline", source: "API3"}
      ]
    };
  },
  methods: {
    configurePipeline(pipeline) {
      this.$router.push("/etl-config");
    }
  }
};
</script>

<style scoped>
.container {
  width: 80%;
  margin: auto;
  padding: 20px;
  background: #f2f2f2;
  border-radius: 10px;
  text-align: center;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #ccc;
  text-align: left;
}

button {
  background-color: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

button:hover {
  color: #007bff;
}
</style>
