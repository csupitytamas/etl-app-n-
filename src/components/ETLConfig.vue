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

    <!-- Forrásfeltöltés csak akkor jelenik meg, ha 'withfile' van kiválasztva -->
    <div class="form-group" v-if="conditions === 'withfile'">
      <label>Own Source feltöltés:</label>
      <!--// TODO: Fájltípus ellenőrzése -->
      <div class="custom-file-input">
        <label for="fileUpload" class="upload-label">
          {{ uploadedFileName || "Click to upload file" }}
        </label>
        <input
            id="fileUpload"
            type="file"
            @change="handleFileUpload"
        />
      </div>
    </div>

    <div class="form-group">
      <label>Field Mapping</label>
      <textarea placeholder="Pl. name -> full_name"></textarea>
    </div>

    <!-- Egyedi transzformáció -->
    <div class="form-group">
      <label>Transformation on the dataset</label>
      <select v-model="transformation">
        <option value="none">None</option>
        <option value="select">Select</option>
        <option value="orderby">OrderBy</option>
        <option value="groupby">GroupBy</option>
        <option value="advenced">Advanced</option>
      </select>
    </div>

    <!-- Adatbázis frissítés -->
    <div class="form-group">
      <label>Dataset update</label>
      <select v-model="update">
        <option value="overwrite">Overwrite</option>
        <option value="append">Append</option>
        <option value="upsert">Upsert (Update and append)</option>
      </select>
    </div>



    <!-- Mentési hely -->
    <div class="form-group">
      <label>Save options</label>
      <select v-model="saveOption">
        <option value="todatabase">Only to database</option>
        <option value="createfile">I need a copy</option>
      </select>
    </div>

    <div class="form-group">
      <button @click="submitPipelineConfig">Save</button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ETLConfig",
  data() {
    return {
      schedule: "daily",
      customTime: "",
      transformation: "none",
      update: "append",
      conditions: "none",
      saveOption: "todatabase",
      uploadedFileName: ""
    };
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      this.uploadedFileName = file ? file.name : "";
    },
    submitPipelineConfig() {
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
.custom-time-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.custom-time-wrapper input[type="time"] {
  width: 150px;
  padding: 6px;
  font-size: 14px;
  border: 1px solid #aaa;
  border-radius: 5px;
  text-align: center;
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
</style>
