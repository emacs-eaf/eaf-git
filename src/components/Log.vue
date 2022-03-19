<template>
  <div class="box">
    <div
      v-for="info in logInfo"
      :key="info.id"
      class="log-item">
      <div
        class="log-id"
        :style="{ 'color': idColor }">
        {{ info.id.slice(0, 7) }}
      </div>
      <div
        class="log-date"
        :style="{ 'color': dateColor }">
        {{ info.time }}
      </div>
      <div
        class="log-author"
        :style="{ 'color': authorColor }">
        {{ info.author }}
      </div>
      <div class="log-message">
        {{ info.message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Log',
  props: {
    logInfo: Array,
    idColor: String,
    dateColor: String,
    authorColor: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .box {
   width: 100%;
   height: 100%;
 }
 
 .log-item {
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 2px;
   padding-bottom: 2px;
   font-size: 16px;
   
   display: flex;
   flex-direction: row;
   align-items: center;
 }
 
 .log-id {
 }
 
 .log-date {
   padding-left: 20px;
 }
 
 .log-author {
   padding-left: 20px;
   width: 20%;
 }
 
 .log-message {
   padding-left: 20px;
   width: 60%;
   
   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
 }
</style>
