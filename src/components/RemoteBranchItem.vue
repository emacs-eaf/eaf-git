<template>
  <div
    :style="{ 'color': source.foregroundColor, 'background': source.backgroundColor }"
    class="item">
    <div>
      {{ source.name }}
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
   },
   methods: {
     
   }
 }
</script>

<style scoped>
 .item {
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 2px;
   padding-bottom: 2px;
   font-size: 16px;
   height: 30px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }
 
 .branch-flag {
   width: 100px;
   padding-left: 10px;
   padding-right: 10px;
 }
</style>
