<template>
  <div
    class="submodule-item"
    :style="{ 'color': source.foregroundColor, 'background': source.backgroundColor }">
    <div class="submodule-name">
      {{ source.name }}
    </div>
    <div class="submodule-date">
      {{ source.date }}
    </div>
    <div class="submodule-hash">
      {{ source.head_id }}
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
 .submodule-item {
   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;
   height: 30px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .submodule-name {
   flex: 1;
 }
 
 .submodule-date {
   padding-right: 20px;
   width: 150px;
 }
 
 .submodule-hash {
   width: 400px;
 }
</style>

