<template>
  <div
    class="log-item"
    :style="{ 'color': source.foregroundColor, 'background': source.backgroundColor }">
    <div class="log-id">
      {{ source.id.slice(0, 7) }}
    </div>
    <div class="log-message">
      {{ source.message }}
    </div>
  </div>
</template>

<script>
 export default {
   name: 'item-component',
   props: {
     index: {
       type: Number
     },
     source: {
       type: Object,
       default () {
         return {}
       }
     }
   }
 }
</script>

<style scoped>
 .log-item {
   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;
   height: 30px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .log-id {
   width: 80px;
 }

 .log-date {
   padding-left: 20px;
   width: 150px;
 }

 .log-author {
   padding-left: 20px;
   width: 150px;

   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
 }

 .log-message {
   padding-left: 20px;
   flex: 1;

   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
   
   width: 100px;
 }
</style>

