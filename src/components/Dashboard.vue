<template>
  <div class="box">
    <div
      v-if="noFileSubmit()"
      class="clean-workspace">
      No file need submitted, clean workspace.
    </div>
    <div v-else>
      <div v-if="unstageFileNumber() > 0">
        <div class="unstaged-title">
          Unstaged changes ({{ unstageStatusInfo.length }})
        </div>
        <div
          v-for="info in unstageStatusInfo"
          :key="info"
          class="item">
          <div class="type">
            {{ info.type }}
          </div>
          <div class="file">
            {{ info.file }}
          </div>
          <br/>
        </div>
      </div>

      <div v-if="stageFileNumber() > 0">
        <div class="staged-title">
          Staged changes ({{ stageStatusInfo.length }})
        </div>
        <div
          v-for="info in stageStatusInfo"
          :key="info"
          class="item">
          <div class="type">
            {{ info.type }}
          </div>
          <div class="file">
            {{ info.file }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
 export default {
   name: 'Dashboard',
   props: {
     stageStatusInfo: Array,
     unstageStatusInfo: Array
   },
   methods: {
     noFileSubmit() {
       return this.unstageFileNumber() + this.stageFileNumber() === 0;
     },
     
     unstageFileNumber() {
       var unstage_files_number = 0;
       if (this.unstageStatusInfo) {
         unstage_files_number = this.unstageStatusInfo.length;
       }
       
       return unstage_files_number;
     },

     stageFileNumber() {
       var stage_files_number = 0;
       if (this.stageStatusInfo) {
         stage_files_number = this.stageStatusInfo.length;
       }
       
       return stage_files_number;
     }
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .box {
   width: 100%;
   height: 100%;
 }

 .item {
   padding-left: 20px;
   padding-right: 10px;
   padding-top: 2px;
   padding-bottom: 2px;
   font-size: 16px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .type {
   padding-right: 10px;
 }

 .clean-workspace {
   padding-left: 10px;
 }
 
 .unstaged-title {
   font-weight: bold;
   padding-left: 10px;
 }

 .staged-title {
   font-weight: bold;
   padding-left: 10px;
 }
</style>
