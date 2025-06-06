<template>
  <div class="dashboard">
    <h2>📊 Dashboard</h2>
    <div class="pipeline" v-for="pipeline in pipelines" :key="pipeline.id">
      <h3>{{ pipeline.name }}</h3>
      <p>Last successful run: <strong>{{ pipeline.lastRun }}</strong></p>
      <p>
        Status:
        <strong :class="{
          'status-success': pipeline.status === 'success',
          'status-failed': pipeline.status === 'failed',
          'status-running': pipeline.status === 'running'
        }">
          {{ pipeline.status }}
        </strong>
      </p>
      <p>Next scheduled run: <strong>{{ pipeline.nextRun }}</strong></p>
      <p>Source: <strong>{{ pipeline.alias }}</strong></p>

      <div class="table-preview" v-if="pipeline.sampleData && pipeline.sampleData.length > 0">
        <table>
          <thead>
            <tr>
              <th v-for="key in tableKeys(pipeline.sampleData[0])" :key="key">{{ key }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in visibleRows(pipeline.sampleData)" :key="index">
              <td v-for="key in tableKeys(row)" :key="key" :data-label="key">{{ row[key] }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="hasMoreRows(pipeline.sampleData)" class="table-ellipsis">
          ...
        </div>
      </div>
      <div v-else>
        <em> No data to display.</em>
      </div>
    </div>
  </div>
</template>

<script>
import { getDashboardPipelines } from "@/api/dashboard";
const MAX_ROWS = 10;

export default {
  name: "DashboardView",
  data() {
    return {
      pipelines: []
    };
  },
  async mounted() {
    try {
      const response = await getDashboardPipelines();
      this.pipelines = response.data;
    } catch (err) {
      console.error("Hiba a dashboard adatok betöltésekor:", err);
    }
  },
  methods: {
    visibleRows(sampleData) {
      return sampleData.slice(0, MAX_ROWS);
    },
    hasMoreRows(sampleData) {
      return sampleData.length > MAX_ROWS;
    },
    tableKeys(row) {
      return Object.keys(row).filter(k => k !== "id");
    }
  }
};
</script>

<style scoped>

.pipeline {
  background: linear-gradient(135deg, #f8fafc 0%, #e9eff6 100%);
  margin: 32px 0;
  padding: 28px 22px;
  border-radius: 14px;
  border: 1.5px solid #b2c1da;
  box-shadow: 0 2px 12px rgba(3, 26, 73, 0.08), 0 1.5px 0.5px rgba(0,0,0,0.02);
  transition: box-shadow 0.2s;
}
.pipeline:hover {
  box-shadow: 0 6px 28px rgba(3, 26, 73, 0.13);
}
.table-preview {
  overflow-x: auto;
  border-radius: 8px;
  background: #fff;
  max-width: 100%;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
  min-width: 120px;
}
@media (max-width: 768px) {
  table, thead, tbody, th, td, tr {
    display: block;
  }
  thead tr {
    display: none;
  }
  td {
    position: relative;
    padding-left: 50%;
    border: none;
    border-bottom: 1px solid #ccc;
  }
  td::before {
    position: absolute;
    top: 8px;
    left: 10px;
    width: 45%;
    white-space: nowrap;
    font-weight: bold;
    content: attr(data-label);
  }
}

.table-ellipsis {
  text-align: center;
  font-size: 3rem;
  color: #031a49;
  font-weight: bold;
}
.status-success { color: green; }
.status-failed { color: red; }
.status-running { color: orange; }
</style>
