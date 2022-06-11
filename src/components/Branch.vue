<template>
  <div class="branch-area"
    :class="[ branchAreaClass ]">
    <Dialog
      :backgroundColor="backgroundColor"
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
      :backgroundColor="backgroundColor"
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

 import { Layout, keepSelectVisible } from "./utils.js"
 
 export default {
   name: 'Branch',
   components: {
     'virtual-list': VirtualList,
     Dialog
   },
   props: {
     layout: String,
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
   computed: {
     branchAreaClass() {
       return this.layout === Layout.Vertical ? "branch-area-vertical" : "branch-area-horizontal";
     }
   },
   mounted() {
     var that = this;
     
     this.selectBranchName = this.localBranchInfo[this.selectBranchIndex].name;

     this.$root.$on("branch_rename", function () {
       window.pyobject.branch_rename(that.selectBranchName);
     });
     
     this.$root.$on("branch_delete", function () {
       window.pyobject.branch_delete(that.selectBranchName);
     });
     
     this.$root.$on("branch_switch", function () {
       window.pyobject.branch_switch(that.selectBranchName);
     });
   },
   beforeDestroy() {
     this.$root.$off("branch_rename");
     this.$root.$off("branch_delete");
     this.$root.$off("branch_switch");
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
 }

 .branch-area-horizontal {
   flex-direction: row;
 }

 .branch-area-vertical {
   flex-direction: column;
 }

 .list {
   z-index: 100;
   overflow-y: scroll;
   height: 100%;
 }
 
 .local-branch {
   /* 70% */
   flex-grow: 7;
 }

 .remote-branch {
   /* 30% */
   flex-grow: 3;
 }
</style>
