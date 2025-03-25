<template>
    <div id="app">
      <router-view></router-view>
    </div>
</template>

<script>
import CreateETLPipeline from "./components/CreateETLPipeline.vue";

export default {
  components: { CreateETLPipeline },
  data() {
    return {
      showETL: false
    };
  },
  methods: {
    showETLWindow() {
      this.showETL = true; // Megjeleníti a komponenst
    }
  }
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 20px;
}
</style>
