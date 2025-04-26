<template>
  <div class="config-container">
    <h2>Configuration</h2>

    <!-- Ütemezés -->
    <div class="form-group">
      <label>Schedule</label>
      <select v-model="schedule">
        <option value="daily">daily</option>
        <option value="hourly">hourly</option>
        <option value="minutes">minutes</option>
        <option value="custom">custom</option>
      </select>
      <div v-if="schedule === 'custom'" class="custom-time-wrapper">
        <input type="time" v-model="customTime" />
      </div>
    </div>

    <!-- Futtatási feltételek -->
  <div class="form-group">
      <label>Running conditions</label>
      <select v-model="conditions">
        <option value="none">None</option>
        <option value="withsource">With different source</option>
        <option value="withdependency">Wait for another pipeline</option>
      </select>
    </div>

    <!-- Dependency selection -->
    <div class="form-group" v-if="conditions === 'withdependency'">
      <label>Select dependency pipeline</label>
      <select v-model="dependencyPipelineId">
        <option value="">None</option>
        <option v-for="pipeline in activePipelines" :key="pipeline.id" :value="pipeline.id">
          {{ pipeline.name }}
        </option>
      </select>
    </div>

    <div class="form-group" v-if="conditions === 'withfile'">
      <label>Own Source feltöltés:</label>
      <div class="custom-file-input">
        <label for="fileUpload" class="upload-label">
          {{ uploadedFileName || "Click to upload file" }}
        </label>
        <input id="fileUpload" type="file" @change="handleFileUpload" />
      </div>
    </div>

    <!-- Field Mapping (Drag & Drop) -->
<div class="form-group">
  <label>Field Mapping</label>
  <draggable v-model="columnOrder" item-key="col" class="draggable-list">
  <template #item="{ element: col,index  }">
    <div class="mapping-row">
        <div class="mapping-header">
          <span class="drag-handle">☰</span>
          <span class="column-index">{{ index + 1 }}.</span>
          <span class="column-name">{{ col }}</span>
          <button class="settings-button" @click="toggleSettings(col)">⚙️</button>
      </div>

        <div v-if="colSettingsOpen[col]" class="mapping-settings">
          <label><input type="checkbox" v-model="fieldMappings[col].rename" /> Rename</label>
          <input v-if="fieldMappings[col].rename" type="text" v-model="fieldMappings[col].newName" placeholder="New name" />

          <label><input type="checkbox" v-model="fieldMappings[col].delete" /> Delete</label>

          <label><input type="checkbox" v-model="fieldMappings[col].split" /> Split</label>
          <input v-if="fieldMappings[col].split" type="text" v-model="fieldMappings[col].separator" placeholder="Separator (,)" />

          <label><input type="checkbox" v-model="fieldMappings[col].join" /> Join</label>
          <div v-if="fieldMappings[col].join" class="join-options">
            <label>Join with column:</label>
            <select v-model="fieldMappings[col].joinColumn">
              <option disabled value="">Please select</option>
              <option v-for="targetCol in allColumns" :key="targetCol" :value="targetCol">
                {{ targetCol }}
              </option>
            </select>

            <label>Join type:</label>
            <select v-model="fieldMappings[col].joinType">
              <option value="inner">Inner Join</option>
              <option value="left">Left Join</option>
              <option value="right">Right Join</option>
              <option value="full">Full Outer Join</option>
            </select>
          </div>
        </div>
      </div>
  </template>
</draggable>
</div>

    <!-- Transformation -->
    <div class="form-group">
      <label>Transformation on the dataset</label>
      <select v-model="transformation">
        <option value="none">None</option>
        <option value="select">Select</option>
        <option value="advenced">Advanced</option>
      </select>
    </div>

    <!-- Select + GroupBy + OrderBy -->
    <div v-if="transformation === 'select'" class="form-group">
      <label>Select columns</label>
      <button class="small-button" @click="toggleSelectAll">
        {{ selectedColumns.length === allColumns.length ? 'Unselect all' : 'Select all' }}
      </button>

      <div class="grid-checkboxes">
        <label v-for="col in allColumns" :key="col">
          <input type="checkbox" :value="col" v-model="selectedColumns" />
          {{ col }}
        </label>
      </div>

      <!-- GROUP BY -->
      <div class="form-group" v-if="selectedColumns.length">
        <label>Group by</label>
        <div class="none-option">
          <input type="checkbox" id="disableGroupBy" v-model="disableGroupBy" />
          <label for="disableGroupBy">None</label>
        </div>
        <div v-if="!disableGroupBy" class="grid-checkboxes">
          <label v-for="col in selectedColumns" :key="'g-' + col">
            <input type="checkbox" :value="col" v-model="groupBy" />
            {{ col }}
          </label>
        </div>
      </div>

      <!-- ORDER BY -->
      <div class="form-group" v-if="selectedColumns.length">
        <label>Order by</label>
        <div class="none-option">
          <input type="checkbox" id="disableOrderBy" v-model="disableOrderBy" />
          <label for="disableOrderBy">None</label>
        </div>
        <div v-if="!disableOrderBy">
          <select v-model="orderBy" class="standard-select">
            <option disabled value="">-- Select column --</option>
            <option v-for="col in selectedColumns" :key="'o-' + col" :value="col">{{ col }}</option>
          </select>

          <div v-if="orderBy" style="margin-top: 10px;">
            <label>Order direction</label>
            <div class="order-direction-container">
              <label><input type="radio" value="asc" v-model="orderDirection" /> Ascending</label>
              <label><input type="radio" value="desc" v-model="orderDirection" /> Descending</label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced (SQL) -->
    <div class="form-group" v-if="transformation === 'advenced'">
      <label>Custom SQL query</label>
      <textarea v-model="customSQL" placeholder="Pl. SELECT name, COUNT(*) FROM table GROUP BY name"></textarea>
    </div>

    <!-- Update mód -->
    <div class="form-group">
      <label>Dataset update</label>
      <select v-model="update">
        <option value="overwrite">Overwrite</option>
        <option value="append">Append</option>
        <option value="upsert">Upsert (Update and append)</option>
      </select>
    </div>

    <!-- Mentés mód -->
    <div class="form-group">
      <label>Save options</label>
      <select v-model="saveOption">
        <option value="todatabase">Database</option>
        <option value="createfile">File</option>
      </select>
    </div>

    <div class="form-group">
      <button @click="submitPipelineConfig">Save</button>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable';

export default {
  name: "ETLConfig",
  components: { draggable },
  data() {
    return {
      schedule: "daily",
      customTime: "",
      transformation: "none",
      update: "append",
      conditions: "none",
      dependencyPipelineId: "",
      activePipelines: [
        { id: "pipeline_1", name: "Daily Import" },
        { id: "pipeline_2", name: "User Sync" },
        { id: "pipeline_3", name: "Revenue Update" },
      ],
      saveOption: "todatabase",
      uploadedFileName: "",

      allColumns: ["name", "email", "age", "country"],
      columnOrder: ["name", "email", "age", "country"],
      selectedColumns: [],
      groupBy: [],
      orderBy: "",
      orderDirection: "asc",
      customSQL: "",

      disableGroupBy: false,
      disableOrderBy: false,

        fieldMappings: {
        name: { rename: false, newName: "", delete: false, split: false, separator: "", join: false, joinColumn: "", joinType: "inner" },
        email: { rename: false, newName: "", delete: false, split: false, separator: "", join: false, joinColumn: "", joinType: "inner" },
        age: { rename: false, newName: "", delete: false, split: false, separator: "", join: false, joinColumn: "", joinType: "inner" },
        country: { rename: false, newName: "", delete: false, split: false, separator: "", join: false, joinColumn: "", joinType: "inner" }
      },
      colSettingsOpen: {},
    };
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      this.uploadedFileName = file ? file.name : "";
    },
    toggleSelectAll() {
      if (this.selectedColumns.length === this.allColumns.length) {
        this.selectedColumns = [];
      } else {
        this.selectedColumns = [...this.allColumns];
      }
    },
      toggleSettings(col) {
      this.colSettingsOpen[col] = !this.colSettingsOpen[col];
    },
    submitPipelineConfig() {
      const payload = {
        schedule: this.schedule,
        custom_time: this.schedule === "custom" ? this.customTime : null,
        transformation: this.transformation,
        columns: {
          select: this.selectedColumns,
          groupby: this.disableGroupBy ? [] : this.groupBy,
          orderby: this.disableOrderBy
            ? null
            : {
                column: this.orderBy,
                direction: this.orderBy ? this.orderDirection : null
              }
        },
        custom_sql: this.transformation === "advenced" ? this.customSQL : null,
        update_mode: this.update,
        save_option: this.saveOption,
        conditions: this.conditions,
        dependency_pipeline_id: this.conditions === "withdependency" ? this.dependencyPipelineId : null,
        uploaded_file_name: this.conditions === "withfile" ? this.uploadedFileName : null
      };

      console.log("Küldendő payload:", payload);
      alert("Pipeline config saved!");
      window.history.back();
    }
  }
};
</script>

<style scoped>
.config-container {
  max-width: 50%;
  margin: 40px auto;
  padding: 40px;
  background-color: #f5f7fa;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  font-family: "Segoe UI", sans-serif;
}

h2 {
  text-align: center;
  font-size: 24px;
  margin-bottom: 32px;
  color: #333;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 24px;
}

label {
  font-weight: 600;
  margin-bottom: 8px;
}
.custom-time-wrapper {
  width: 100%;
  display: flex;
  justify-content: center; /* Ez hozza középre az inputot */
  margin-top: 10px;
}

.custom-time-wrapper input[type="time"] {
  width: 50%; /* vagy 60%, ha keskenyebb kell */
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #aaa;
  border-radius: 5px;
  background-color: white;
  box-sizing: border-box;
  text-align: center; /* az érték is középen jelenik meg */
}

input[type="text"],
input[type="time"],
input[type="file"],
textarea,
select {
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #bbb;
  font-size: 14px;
  min-width: 200px;
  text-align: center;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

button {
  background-color: #007bff;
  color: white;
  padding: 12px 20px;
  font-size: 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
}

button:hover {
  background-color: #0056b3;
}

.small-button {
  padding: 6px 14px;
  font-size: 13px;
  align-self: flex-start;
  margin-bottom: 8px;
}

.custom-file-input {
  position: relative;
  width: 100%;
}

.upload-label {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px dashed #007bff;
  border-radius: 6px;
  background-color: #e9f1ff;
  color: #007bff;
  text-align: center;
  cursor: pointer;
  font-size: 14px;
}

.custom-file-input input[type="file"] {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  height: 100%;
  width: 100%;
  cursor: pointer;
}

.none-option {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}

.grid-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  margin-top: 10px;
}
.grid-checkboxes label {
  display: flex;
  align-items: center;
  gap: 6px;
}
.order-direction-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 10px;
}
.standard-select {
  width: 100%;
  padding: 8px 10px;
  font-size: 14px;
  border: 1px solid #aaa;
  border-radius: 5px;
  background-color: white;
  text-align: center;
}

/* Drag & Drop */

.draggable-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-start;
}

.mapping-row {
  width: clamp(200px, 18%, 250px);
  background: #ffffff;
  border: 1px dashed #bbb;
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.mapping-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 6px;
}

.column-index {
  font-weight: bold;
  font-size: 14px;
  color: #888;
}

.mapping-settings {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  box-sizing: border-box;
  overflow-wrap: break-word;
}

.mapping-settings input[type="text"],
.mapping-settings select {
  width: 100%;
  max-width: 190px;
  padding: 6px 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}

.join-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.join-options label {
  font-weight: 500;
}

.join-options select {
  text-align: center;
  min-width: 100px;
  max-width: 180px;
  align-self: flex-start;
}

.settings-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

.drag-handle {
  cursor: grab;
}
</style>
