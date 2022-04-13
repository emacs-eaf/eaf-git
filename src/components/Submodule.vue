<template>
  <div class="box">
    <Dialog 
      :title="dialogTitle">
      <virtual-list
        v-if="submoduleInfo.length > 0"
        ref="submodulelist"
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="submoduleInfo"
        :data-component="submoduleItemComponent"/>
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
 import SubmoduleItem from './SubmoduleItem'
 import VirtualList from 'vue-virtual-scroll-list'

 export default {
   name: 'Submodule',
   components: {
     'virtual-list': VirtualList,
     Dialog
   },
   props: {
     submoduleInfo: Array,
     backgroundColor: String,
     selectColor: String,
     currentSubmoduleIndex: Number,
     pyobject: Object
   },
   data() {
     return {
       submoduleItemComponent: SubmoduleItem,
       currentPageElementNum: 0
     }
   },
   computed: {
     dialogTitle() {
       return "Submodule (" + this.submoduleInfo.length + ")";
     }
   },
   watch: {
     currentSubmoduleIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.submoduleInfo.length > 0) {
           this.keepSelectVisible();
         }
       }
     },
   },
   mounted() {
     var that = this;
     
     this.$root.$on("submoduleAdd", function () {
       that.pyobject.submodule_add();
     });

     this.$root.$on("submoduleRemove", function () {
       that.pyobject.submodule_remove(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });

     this.$root.$on("submoduleUpdate", function () {
       that.pyobject.submodule_remove(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });
     
     this.$root.$on("submoduleSelectPgUp", function () {
       that.submoduleSelectPgUp();
     });

     this.$root.$on("submoduleSelectPgDn", function () {
       that.submoduleSelectPgDn();
     });
   },
   beforeDestroy() {
     this.$root.$off("submoduleAdd");
     this.$root.$off("submoduleRemove");
     this.$root.$off("submoduleUpdate");
     this.$root.$off("submoduleSelectPgUp");
     this.$root.$off("submoduleSelectPgDn");
   },
   methods: {
     keepSelectVisible() {
       var submodulelist = this.$refs.submodulelist;
       var itemHeight = submodulelist.getSize(0);
       var currentOffsetY = itemHeight * this.currentSubmoduleIndex;
       var viewHeight = submodulelist.getClientSize();
       var offset = submodulelist.getOffset();

       if (currentOffsetY + itemHeight > offset + viewHeight) {
         submodulelist.scrollToOffset(currentOffsetY - viewHeight + itemHeight);
       } else if (currentOffsetY < offset) {
         submodulelist.scrollToOffset(currentOffsetY);
       }
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
       var submodulelist = this.$refs.submodulelist;
       var itemHeight = submodulelist.getSize(0);
       var viewHeight = submodulelist.getClientSize();

       this.currentPageElementNum = Math.floor(viewHeight / itemHeight);
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
