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
         this.selectBranch = this.branchInfo[this.selectBranchIndex];
         this.keepSelectVisible();
       },
       deep: true
     }
   },
   data() {
     return {
       branchItemComponent: BranchItem,
       selectBranch: {}
     }
   },
   mounted() {
     this.selectBranch = this.currentBranch;

     var that = this;

     this.$root.$on("branchNew", function () {
       window.pyobject.branch_new();
     });

     this.$root.$on("branchDelete", function () {
       window.pyobject.branch_delete([that.selectBranch]);
     });
     
     this.$root.$on("branchSwitch", function () {
       window.pyobject.branch_switch([that.selectBranch]);
     });
   },
   beforeDestroy() {
     this.$root.$off("branchNew");
     this.$root.$off("branchDelete");
     this.$root.$off("branchSwitch");
   },
   methods: {
     keepSelectVisible() {
       var branchlist = this.$refs.branchlist;
       var itemHeight = branchlist.getSize(0);
       var currentOffsetY = itemHeight * this.selectBranchIndex;
       var viewHeight = branchlist.getClientSize();
       var offset = branchlist.getOffset();

       if (currentOffsetY + itemHeight > offset + viewHeight) {
         branchlist.scrollToOffset(currentOffsetY - viewHeight + itemHeight);
       } else if (currentOffsetY < offset) {
         branchlist.scrollToOffset(currentOffsetY);
       }
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

 .list {
   z-index: 100;
   max-height: calc(100vh - 150px);
   overflow-y: scroll;
 }
</style>
