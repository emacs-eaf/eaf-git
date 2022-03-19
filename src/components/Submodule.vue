<template>
  <div class="box">
    <div v-if="submoduleInfo.length > 0">
      <div
        v-for="info in submoduleInfo"
        :key="info"
        class="item">
        {{ info }}
      </div>
    </div>
    <div
      v-else
      class="notify">
      No submodule found in current repository.
    </div>
  </div>
</template>

<script>
 export default {
   name: 'Submodule',
   props: {
     submoduleInfo: Array
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

 .notify {
   font-size: 16px;
   text-align: center;
   justify-self: center;
   margin: auto;
   font-size: 18px;
 }
</style>
