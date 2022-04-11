<template>
  <div class="box">
    <Dialog title="Submodule">
      <div
        v-if="submoduleInfo.length > 0"
        class="list"
        ref="submodules">
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
    </Dialog>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"

 export default {
   name: 'Submodule',
   components: {
     Dialog
   },
   props: {
     submoduleInfo: Array,
     backgroundColor: String,
     selectColor: String,
     currentSubmoduleIndex: Number
   },
   data() {
     return {
       currentPageElementNum: 0
     }
   },
   watch: {
     currentSubmoduleIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.submoduleInfo.length > 0) {
           this.updateItemBackground(oldVal, val);
           this.keepSelectVisible();
         }
       }
     },
   },
   mounted() {
     var that = this;
     
     this.showHighlightLine();

     this.$root.$on("submoduleSelectPgUp", function () {
       that.submoduleSelectPgUp();
     });

     this.$root.$on("submoduleSelectPgDn", function () {
       that.submoduleSelectPgDn();
     });
   },
   beforeDestroy() {
     this.$root.$off("submoduleSelectPgUp");
     this.$root.$off("submoduleSelectPgDn");
   },
   methods: {
     showHighlightLine() {
       if (this.currentSubmoduleIndex !== null && this.currentSubmoduleIndex >= 0) {
         this.$refs.submodules.children[this.currentSubmoduleIndex].style.background = this.selectColor;
       }

       this.keepSelectVisible();
     },

     updateItemBackground(oldIndex, newIndex) {
       if (oldIndex !== null && oldIndex >= 0) {
         var oldItem = this.$refs.submodules.children[oldIndex];
         oldItem.style.background = this.backgroundColor;
       }

       if (newIndex !== null && newIndex >= 0) {
         var newItem = this.$refs.submodules.children[newIndex];
         newItem.style.background = this.selectColor;
       }
     },

     keepSelectVisible() {
       /* Use nextTick wait DOM update, then make sure current file in visible area. */
       this.$nextTick(function() {
         var selectLog = this.$refs.submodules.children[this.currentSubmoduleIndex]
         if (selectLog !== undefined) {
           selectLog.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
         }
       })
     },
     
     submoduleSelectPgUp() {
       this.refreshSceenElementNumber()
       this.$emit("updateSubmoduleIndex", this.currentSubmoduleIndex - this.currentPageElementNum);
     },

     submoduleSelectPgDn() {
       this.refreshSceenElementNumber()
       this.$emit("updateSubmoduleIndex", this.currentSubmoduleIndex + this.currentPageElementNum);
     },

     refreshSceenElementNumber() {
       var that = this;
       
       this.$nextTick(() => {
         var submoduleList = that.$refs.submodules;
         var selectSubmodule = that.$refs.submodules.children[that.currentSubmoduleIndex];
         if (submoduleList !== undefined && selectSubmodule !== undefined) {
           that.currentPageElementNum = Math.floor(submoduleList.clientHeight / selectSubmodule.clientHeight);
         }
       });
     },
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
   display: flex;
   flex-direction: row;
   align-items: center;

   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;
   height: 30px;
 }

 .notify {
   display: flex;
   flex-direction: column;
   justify-content: center;

   height: 100%;

   font-size: 16px;
   text-align: center;
   justify-self: center;
   margin: auto;
   font-size: 20px;
 }

 .list {
   z-index: 100;
   max-height: calc(100vh - 150px);
   overflow-y: scroll;
 }
</style>
