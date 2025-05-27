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

    <div class="form-group" v-if="conditions === 'withsource'">
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
      <template #item="{ element: col, index }">
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
            <select v-if="fieldMappings[col].split" v-model="fieldMappings[col].separator">
              <option disabled value="">Please select</option>
              <option v-for="sep in separatorOptions" :key="sep" :value="sep">{{ sep === ' ' ? 'space' : sep }}</option>
            </select>

            <label><input type="checkbox" v-model="fieldMappings[col].concat.enabled" /> Concatenate</label>
            <div v-if="fieldMappings[col].concat.enabled" class="join-options">
              <label>With column:</label>
              <select v-model="fieldMappings[col].concat.with">
                <option disabled value="">Please select</option>
                <option v-for="targetCol in allColumns" :key="targetCol" :value="targetCol">
                  {{ targetCol }}
                </option>
              </select>

              <label>Separator:</label>
              <select v-model="fieldMappings[col].concat.separator">
                <option disabled value="">Please select</option>
                <option v-for="sep in separatorOptions" :key="sep" :value="sep">{{ sep === ' ' ? 'space' : sep }}</option>
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

<script lang="ts">
import draggable from 'vuedraggable';
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { usePipelineStore } from '@/stores/pipelineStore';

export default defineComponent({
  name: 'ETLConfig',
  components: { draggable },
  setup() {
    const store = usePipelineStore();
    const router = useRouter();
    return { store, router };
  },
  data() {
    return {
      schedule: this.store.config.schedule || 'daily',
      customTime: this.store.config.custom_time || '',
      conditions: this.store.config.condition || 'none',
      dependencyPipelineId: this.store.config.dependency_pipeline_id || '',
      update: this.store.config.update_mode || 'append',
      saveOption: this.store.config.save_option || 'todatabase',
      uploadedFileName: this.store.config.uploaded_file_name || '',
      fileData: null as File | null,

      activePipelines: [
        { id: 'pipeline_1', name: 'Daily Import' },
        { id: 'pipeline_2', name: 'User Sync' },
        { id: 'pipeline_3', name: 'Revenue Update' },
      ],

      allColumns: ["name", "email", "age", "country"],
      columnOrder: ["name", "email", "age", "country"],
      selectedColumns: [],
      groupBy: [],
      orderBy: "",
      orderDirection: "asc",
      customSQL: "",
      transformation: "none",

      disableGroupBy: false,
      disableOrderBy: false,

      fieldMappings: {
        name: { rename: false, newName: "", delete: false, split: false, separator: "", concat: { enabled: false, with: "", separator: " " } },
        email: { rename: false, newName: "", delete: false, split: false, separator: "", concat: { enabled: false, with: "", separator: " " } },
        age: { rename: false, newName: "", delete: false, split: false, separator: "", concat: { enabled: false, with: "", separator: " " } },
        country: { rename: false, newName: "", delete: false, split: false, separator: "", concat: { enabled: false, with: "", separator: " " } }
      },

      colSettingsOpen: {} as Record<string, boolean>,
      separatorOptions: [" ", ",", ";", "-", "/", ":", "_"]
    };
  },
  mounted() {
    console.log("Érkezett query paraméterek:", this.$route.query);
  },
  methods: {
    handleFileUpload(event: Event) {
      const file = (event.target as HTMLInputElement).files?.[0] || null;
      if (file) {
        this.uploadedFileName = file.name;
        this.fileData = file;
      }
    },
    toggleSelectAll() {
      if (this.selectedColumns.length === this.allColumns.length) {
        this.selectedColumns = [];
      } else {
        this.selectedColumns = [...this.allColumns];
      }
    },
    toggleSettings(col: string) {
      this.colSettingsOpen[col] = !this.colSettingsOpen[col];
    },
    submitPipelineConfig() {
      // Ellenőrzés: fájl kötelező, ha withsource
      if (this.conditions === 'withsource' && !this.fileData) {
        alert('Please upload a source file!');
        return;
      }

      // Mentés store-ba
      this.store.config = {
        ...this.store.config,
        schedule: this.schedule,
        custom_time: this.schedule === 'custom' ? this.customTime : null,
        condition: this.conditions,
        dependency_pipeline_id: this.conditions === 'withdependency' ? this.dependencyPipelineId : null,
        uploaded_file_name: this.conditions === 'withsource' ? this.uploadedFileName : null,

        update_mode: this.update,
        save_option: this.saveOption,

        field_mappings: this.fieldMappings,
        column_order: this.columnOrder,
        selected_columns: this.selectedColumns,
        group_by_columns: this.disableGroupBy ? [] : this.groupBy,
        order_by_column: this.disableOrderBy ? null : this.orderBy,
        order_direction: this.disableOrderBy ? null : this.orderDirection,
        custom_sql: this.transformation === 'advenced' ? this.customSQL : null,
        transformation: this.transformation
      };

      this.router.push('/create-etl');
    }
  }
});
</script>

<style scoped src="./ETLConfig.style.css"></style>
