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
        <option value="withsource">with different source</option>
        <option value="withfile">with my file</option>
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
      <draggable v-model="columnOrder" item-key="name" class="draggable-list">
        <template #item="{ element: col }">
          <div class="mapping-row">
            <span class="drag-handle">☰</span>
            <span>{{ col }}</span>
            <input type="text" v-model="fieldMappings[col].newName" placeholder="New name" />

            <label><input type="checkbox" v-model="fieldMappings[col].delete" /> Delete</label>
            <label><input type="checkbox" v-model="fieldMappings[col].split" /> Split</label>
            <input v-if="fieldMappings[col].split" type="text" v-model="fieldMappings[col].separator" placeholder="Separator (,)" />

            <label><input type="checkbox" v-model="fieldMappings[col].join" /> Join</label>
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
          <select v-model="orderBy">
            <option disabled value="">-- Select column --</option>
            <option v-for="col in selectedColumns" :key="'o-' + col" :value="col">{{ col }}</option>
          </select>

          <div v-if="orderBy" style="margin-top: 10px;">
            <label>Order direction</label>
            <div class="grid-checkboxes">
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
        name: { newName: "", delete: false, split: false, separator: "", join: false },
        email: { newName: "", delete: false, split: false, separator: "", join: false },
        age: { newName: "", delete: false, split: false, separator: "", join: false },
        country: { newName: "", delete: false, split: false, separator: "", join: false }
      }
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
        uploaded_file_name: this.conditions === "withfile" ? this.uploadedFileName : null
      };

      console.log("Küldendő payload:", payload);
      alert("Pipeline config saved!");
    }
  }
};
</script>

<style scoped>
.config-container {
  width: 60%;
  max-width: 800px;
  margin: 30px auto;
  padding: 25px;
  background-color: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #ccc;
  font-family: "Segoe UI", sans-serif;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 6px;
  font-weight: 600;
}

input[type="text"],
input[type="time"],
input[type="file"],
textarea,
select {
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #aaa;
  font-size: 14px;
}

textarea {
  resize: vertical;
  min-height: 60px;
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

.custom-file-input {
  position: relative;
  display: inline-block;
  width: 100%;
}

.upload-label {
  display: block;
  width: 100%;
  padding: 10px;
  border: 1px dashed #007bff;
  border-radius: 5px;
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

.small-button {
  padding: 4px 10px;
  font-size: 13px;
  margin-bottom: 8px;
  align-self: flex-start;
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
}

.grid-checkboxes label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.mapping-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border: 1px dashed #ccc;
  border-radius: 6px;
  background: #fefefe;
  margin-bottom: 6px;
}

.drag-handle {
  cursor: grab;
}
</style>
