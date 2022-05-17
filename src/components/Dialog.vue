<template>
  <div class="dialog">
    <div
      class="title"
      :style="{ 'background': backgroundColor }">
      {{ title }}
    </div>
    <div class="frame">
      <slot/>
    </div>
  </div>
</template>

<script>
 export default {
   name: 'Dialog',
   props: {
     title: String,
     backgroundColor: String,
     hasScrollChild: Boolean
   },
   methods: {
     dialogBoxHeight() {
       if (this.hasScrollChild) {
         return "";
       } else {
         return "100%";
       }
     }
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .dialog {
   position: relative;

   width: 100%;
   height: 100%;
 }

 .frame {
   position: absolute;
   left: 10px;
   top: 10px;
   right: 10px;
   bottom: 10px;

   border: 1px solid;
   border-radius: 5px;

   padding-left: 10px;
   padding-right: 10px;
   padding-top: 20px;
   padding-bottom: 20px;

   overflow-y: scroll;
 }

 .title {
   position: absolute;
   left: 30px;
   top: 0px;

   padding-left: 5px;
   padding-right: 5px;

   z-index: 999;
 }
</style>
