<template>
  <div class="box">
    <Dialog title="Branch">
      <virtual-list
        ref="branchlist"
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="branchInfo"
        :data-component="branchItemComponent"/>
    </Dialog>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"
 import BranchItem from './BranchItem'
 import VirtualList from 'vue-virtual-scroll-list'

 import { keepSelectVisible } from "./utils.js"
 
 export default {
   name: 'Branch',
   components: {
     'virtual-list': VirtualList,
     Dialog
   },
   props: {
     selectBranchIndex: Number,
     currentColor: String,
     backgroundColor: String,
     selectColor: String,
     currentBranch: String,
     branchInfo: Array
   },
   watch: {
     selectBranchIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         this.selectBranchName = this.branchInfo[this.selectBranchIndex].name;
         keepSelectVisible(this.$refs.branchlist, val);
       },
       deep: true
     }
   },
   data() {
     return {
       branchItemComponent: BranchItem,
       selectBranchName: ""
     }
   },
   mounted() {
     var that = this;
     
     this.selectBranchName = this.currentBranch;
     
     this.$root.$on("branchNew", function () {
       window.pyobject.branch_new();
     });

     this.$root.$on("branchDelete", function () {
       window.pyobject.branch_delete(that.selectBranchName);
     });
     
     this.$root.$on("branchSwitch", function () {
       window.pyobject.branch_switch(that.selectBranchName);
     });
   },
   beforeDestroy() {
     this.$root.$off("branchNew");
     this.$root.$off("branchDelete");
     this.$root.$off("branchSwitch");
   },
   methods: {
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .box {
   width: 100%;
   height: 100%;
 }

 .list {
   z-index: 100;
   max-height: calc(100vh - 150px);
   overflow-y: scroll;
 }
</style>
