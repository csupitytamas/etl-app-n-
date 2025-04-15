<template>
  <div class="dashboard">
    <h2>📊  Dashboard</h2>

    <div class="pipeline" v-for="pipeline in pipelines" :key="pipeline.id">
      <h3>{{ pipeline.name }}</h3>
      <p>Last successful run: <strong>{{ pipeline.lastRun }}</strong></p>
      <p> Status: <strong>{{ pipeline.status }}</strong></p>
      <p> Next scheduled run: <strong>{{ pipeline.nextRun }}</strong></p>
      <p> Source: <strong>{{ pipeline.source }}</strong></p>

      <div class="table-preview">
        <table>
          <thead>
          <tr>
            <th v-for="(value, key) in pipeline.sampleData[0]" :key="key">{{ key }}</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(row, index) in pipeline.sampleData" :key="index">
            <td v-for="(value, key) in row" :key="key" :data-label="key">{{ value }}</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DashboardView",
  data() {
    return {
      pipelines: [
        {
          id: 1,
          name: "My Pipeline",
          lastRun: "2025-03-29 22:00",
          status: "Completed",
          nextRun: "2025-03-30 22:00",
          source: "API2",
          sampleData: [
            {  id: 2,
              productName: "Wireless Mouse",
              category: "Accessories",
              price: 25.99,
              stock: 150,
              soldLastWeek: 32,
              warehouse: "A1",
              supplier: "LogiTech",
              restockThreshold: 20,
              weightKg: 0.2,
              dimensions: "10x6x4 cm",
              color: "Black",
              rating: 4.5},
            { id: 2,
              productName: "USB-C Hub",
              category: "Adapters",
              price: 39.99,
              stock: 80,
              soldLastWeek: 18,
              warehouse: "B3",
              supplier: "Anker",
              restockThreshold: 15,
              weightKg: 0.1,
              dimensions: "12x3x2 cm",
              color: "Gray",
              rating: 4.7}
          ]
        },
        {
          id:5,
          name: "Your Pipeline",
          lastRun: "2025-03-30 08:00",
          status: " Running",
          nextRun: "2025-03-30 20:00",
          source: "API1",
          sampleData: [
            { id: 101, product: "Widget X", stock: 22 },
            { id: 102, product: "Widget Y", stock: 18 }
          ]
        }
      ]
    };
  }
};
</script>

<style scoped>
.table-preview {
  overflow-x: auto;
}
.dashboard {
  padding: 20px;
  font-family: "Segoe UI", sans-serif;
}
.pipeline {
  background: #f2f2f2;
  margin: 20px 0;
  padding: 20px;
  border-radius: 8px;
}
.table-preview {
  margin-top: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
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
    content: attr(data-label); /* ezt JS-ből vagy Vue-ból meg kell adni */
  }
}
</style>
