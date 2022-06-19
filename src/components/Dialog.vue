<template>
  <fieldset class="dialog">
    <legend
      class="title"
      :style="{ 'background': backgroundColor }">
      {{ title }}
    </legend>
    <div class="frame collapsible"
      :class="{ collapsed: collapsed }">
      <slot/>
    </div>
  </fieldset>
</template>

<script>
 export default {
   name: 'Dialog',
   props: {
     title: String,
     backgroundColor: String,
     collapsed: Boolean,
   },
   methods: {
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .dialog {
   border: 1px solid;
   border-radius: 5px;

   padding-left: 10px;
   padding-right: 10px;
   padding-top: 20px;
   padding-bottom: 20px;

   flex: 1;
   display: flex;
   flex-direction: column;

   overflow-y: scroll;
 }

 .frame {
   flex: 1;
  /*
   overflow-y: scroll;
  */
 }

 .title {
   left: 30px;
   top: 0px;

   padding-left: 5px;
   padding-right: 5px;
 }
</style>
