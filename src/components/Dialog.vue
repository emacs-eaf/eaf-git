<template>
  <div
    class="dialog-box"
    :style="{ 'height': dialogBoxHeight() }">
    <fieldset class="dialog-fieldset">
      <legend class="dialog-title">{{ title }}</legend>
      <slot/>
    </fieldset>
  </div>
</template>

<script>
 export default {
   name: 'Dialog',
   props: {
     title: String,
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
 .dialog-box {
   padding: 10px;
 }

 .dialog-fieldset {
   border: 1px solid;
   border-radius: 5px;
   height: 100%;
   width: 100%;
 }

 .dialog-title {
   margin-left: 1em;
   padding: 0.2em 0.8em
 }
 
 fieldset {
   margin-inline-start: 0;
   margin-inline-end: 0;
   padding-block-start: 0;
   padding-inline-start: 0;
   padding-inline-end: 0;
   padding-block-end: 0;
   min-inline-size: min-content;   
 }
</style>
