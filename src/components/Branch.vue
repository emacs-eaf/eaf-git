<template>
  <div class="box">
    <div
      v-for="info in branchInfo"
      :key="info"
      class="item">
      {{ info }}
    </div>
  </div>
</template>

<script>
 export default {
   name: 'Branch',
   props: {
     branchInfo: Array
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
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 2px;
   padding-bottom: 2px;
   font-size: 16px;
 }
</style>
