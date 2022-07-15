<template>
  <div id="app">
    <Main/>
  </div>
</template>

<script>
 import Main from './components/Main.vue'

 export default {
   name: 'App',
   components: {
     Main
   },
   mounted() {
   }
 }
</script>

<style>
 /* to fix some weird flex isues */
 * {
   min-height: 0px;
   min-width: 0px;
 }

 #app {
   display: flex;
   flex-direction: column;
   align-items: center;
   justify-content: center;
   width: 100%;
   height: 100%;
 }

 html, body {
   width: 100%;
   height: 100%;
   margin: 0;
   padding: 0;
 }

 .layout-horizontal {
   flex-direction: row;
 }

 .layout-vertical {
   flex-direction: column;
 }

 .collapsible.collapsed > .collapsible-item {
   display: none;
 }
 
 .layout-horizontal > *:not(:last-child) {
   margin-right: 10px;
 }

 .layout-vertical > *:not(:last-child) {
   margin-bottom: 10px;
 }
</style>
