<template>
  <div class="branch-area">
    <Dialog
      class="local-branch"
      title="Local Branch">
      <virtual-list
        ref="branchlist"
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="localBranchInfo"
        :data-component="localBranchItemComponent"/>
    </Dialog>
    <Dialog
      class="remote-branch"
      title="Remote Branch">
      <virtual-list
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="remoteBranchInfo"
        :data-component="remoteBranchItemComponent"/>
    </Dialog>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"
 import LocalBranchItem from './LocalBranchItem'
 import RemoteBranchItem from './RemoteBranchItem'
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
     localBranchInfo: Array,
     remoteBranchInfo: Array
   },
   watch: {
     selectBranchIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         this.selectBranchName = this.localBranchInfo[this.selectBranchIndex].name;
         keepSelectVisible(this.$refs.branchlist, val);
       },
       deep: true
     }
   },
   data() {
     return {
       localBranchItemComponent: LocalBranchItem,
       remoteBranchItemComponent: RemoteBranchItem,
       selectBranchName: ""
     }
   },
   mounted() {
     var that = this;
     
     this.selectBranchName = this.localBranchInfo[this.selectBranchIndex].name;
     
     this.$root.$on("branch_delete", function () {
       window.pyobject.branch_delete(that.selectBranchName);
     });
     
     this.$root.$on("branch_switch", function () {
       window.pyobject.branch_switch(that.selectBranchName);
     });
   },
   beforeDestroy() {
     this.$root.$off("js_branch_delete");
     this.$root.$off("js_branch_switch");
   },
   methods: {
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .branch-area {
   width: 100%;
   height: 100%;
   
   display: flex;
   flex-direction: row;
   
   max-height: calc(100vh - 110px);
 }

 .list {
   z-index: 100;
   max-height: calc(100vh - 150px);
   overflow-y: scroll;
 }
 
 .local-branch {
   width: 70%;
 }

 .remote-branch {
   width: 30%;
 }
</style>
