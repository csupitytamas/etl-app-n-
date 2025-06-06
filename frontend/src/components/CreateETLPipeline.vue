<template>
  <div class="container">
    <h2>Create New ETL Pipeline</h2>

    <form @submit.prevent="submitPipeline" class="form-layout">
      <div class="form-row">
        <label for="pipelineName">Pipeline Name:</label>
        <input v-model="pipelineName" type="text" id="pipelineName" placeholder="Enter pipeline name" required />
      </div>

      <div class="form-row">
        <label for="source">Select Source:</label>
        <select v-model="selectedSource" id="source">
          <option disabled value="">Please select</option>
          <option
            v-for="item in sources"
            :key="item.source"
            :value="item.source"
            :title="item.description || ''"
          >
            {{ item.alias || item.source }}
          </option>
        </select>
      </div>

      <div class="button-row">
        <button type="button" class="secondary" @click="openConfiguration">Configuration</button>
        <button type="submit" class="primary">Create Pipeline</button>
      </div>
    </form>
  </div>
</template>

<script>
import {createPipeline, getAvailableSources} from '@/api/pipeline'
import { usePipelineStore } from '@/stores/pipelineStore';


export default {
  data() {
    return {
      sources: [],
    };
  },
  computed: {
    store() {
      return usePipelineStore();
    },
    pipelineName: {
      get() {
        return this.store.pipeline_name;
      },
      set(value) {
        this.store.pipeline_name = value;
      }
    },

    selectedSource: {
      get() {
        return this.store.source;
      },
      set(value) {
        this.store.source = value;
      }
    }
  },


  mounted() {
  this.fetchSources();
},


  methods: {
    async fetchSources() {
  try {
    const response = await getAvailableSources();
    console.log("Sources fetched:", response.data); // <--- EZ FONTOS
    this.sources = response.data;
  } catch (err) {
    console.error("Can't load the sources:", err);
  }
},


submitPipeline() {
  const payload = {
    pipeline_name: this.pipelineName,
    source: this.selectedSource,
    ...this.store.config
  };
  console.log("Final payload:", payload);
  createPipeline(payload)
    .then(response => {
      alert('Successfully created!');
      this.$router.push('/');
    })
    .catch(error => {
      alert('Error!');
    });
},


    openConfiguration() {
      this.$router.push({
        path: "/etl-config",
        query: {
          pipelineName: this.pipelineName,
          selectedSource: this.selectedSource,
        }
      });
    }
  }
};
</script>
<style scoped src="./styles/CreateETLPipeline.style.css"></style>
