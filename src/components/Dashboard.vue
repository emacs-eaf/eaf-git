<template>
  <div class="box">
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
    </div>
    
    <br/>
    
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
</template>

<script>
 export default {
   name: 'Dashboard',
   props: {
     stageStatusInfo: Array,
     unstageStatusInfo: Array
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
 
 .unstaged-title {
   font-weight: bold;
   padding-left: 10px;
 }

 .staged-title {
   font-weight: bold;
   padding-left: 10px;
 }
</style>
