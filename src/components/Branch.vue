<template>
  <div class="box">
    <div
      v-for="info in branchInfo"
      :key="info"
      :style="{ 'color': itemForegroundColor(info), 'background': itemBacakgroundColor(info) }"
      class="item">
      <div class="branch-flag">
        {{ currentBranchText(info) }}
      </div>
      <div>
        {{ info }}
      </div>
    </div>
  </div>
</template>

<script>
 export default {
   name: 'Branch',
   props: {
     currentColor: String,
     backgroundColor: String,
     selectColor: String,
     currentBranch: String,
     branchInfo: Array
   },
   watch: {
     selectIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         this.selectBranch = this.branchInfo[this.selectIndex];
       },
       deep: true
     }
   },
   data() {
     return {
       selectBranch: "",
       selectIndex: 0
     }
   },
   mounted() {
     this.selectBranch = this.currentBranch;
     this.selectIndex = this.branchInfo.indexOf(this.selectBranch);

     var that = this;

     this.$root.$on("branchSelectNext", function () {
       that.branchSelectNext();
     });

     this.$root.$on("branchSelectPrev", function () {
       that.branchSelectPrev();
     });

     this.$root.$on("branchSelectLast", function () {
       that.branchSelectLast();
     });

     this.$root.$on("branchSelectFirst", function () {
       that.branchSelectFirst();
     });

     this.$root.$on("branchNew", function () {
       window.pyobject.branch_new();
     });

     this.$root.$on("branchDelete", function () {
       window.pyobject.branch_delete(that.selectBranch);
     });
     
     this.$root.$on("branchSwitch", function () {

     });
   },
   beforeDestroy() {
     this.$root.$off("branchSelectNext");
     this.$root.$off("branchSelectPrev");
     this.$root.$off("branchSelectLast");
     this.$root.$off("branchSelectFirst");
     this.$root.$off("branchSwitch");
   },
   methods: {
     currentBranchText(branch) {
       if (branch === this.currentBranch) {
         return "[current]"
       } else {
         return "";
       }
     },

     itemForegroundColor(branch) {
       if (branch === this.currentBranch) {
         return this.currentColor;
       } else {
         return "";
       }
     },

     itemBacakgroundColor(branch) {
       if (branch === this.selectBranch) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
       }
     },

     branchSelectNext() {
       if (this.selectIndex < this.branchInfo.length - 1) {
         this.selectIndex += 1;
       }
     },

     branchSelectPrev() {
       if (this.selectIndex > 0) {
         this.selectIndex -= 1;
       }
     },

     branchSelectLast() {
       this.selectIndex = this.branchInfo.length - 1;
     },

     branchSelectFirst() {
       this.selectIndex = 0;
     }
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
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 2px;
   padding-bottom: 2px;
   font-size: 16px;
   height: 30px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }
 
 .branch-flag {
   width: 100px;
   padding-left: 10px;
   padding-right: 10px;
 }
</style>
