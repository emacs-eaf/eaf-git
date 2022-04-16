<template>
  <div class="log-box">
    <Dialog
      class="flex-expand"
      :title="logTitle"
      hasScrollChild="true">
      <virtual-list
        ref="loglist"
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="logInfo"
        :data-component="logItemComponent"/>
    </Dialog>

    <Dialog
      v-if="compareLogInfo.length > 0"
      class="compare-log-list"
      :title="compareLogTitle"
      hasScrollChild="true">
      <virtual-list
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="compareLogInfo"
        :data-component="compareLogItemComponent"/>
    </Dialog>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"

 import LogItem from './LogItem'
 import CompareLogItem from './CompareLogItem'
 import VirtualList from 'vue-virtual-scroll-list'
 
 import { keepSelectVisible, getListPageElementNumber } from "./utils.js"

 export default {
   name: 'Log',
   components: {
     'virtual-list': VirtualList,
     Dialog
   },
   props: {
     logBranch: String,
     logInfo: Array,
     compareLogBranch: String,
     compareLogInfo: Array,
     idColor: String,
     dateColor: String,
     authorColor: String,
     backgroundColor: String,
     selectColor: String,
     markColor: String,
     matchColor: String,
     currentLogIndex: Number,
     searchLogKeyword: String,
     searchLogMatchNumber: Number,
     searchLogIndex: Number,
     pyobject: Object
   },
   data() {
     return {
       logItemComponent: LogItem,
       compareLogItemComponent: CompareLogItem,
       currentPageElementNum: 0
     }
   },
   watch: {
     currentLogIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           keepSelectVisible(this.$refs.loglist, val);
         }
       }
     },
   },
   computed: {
     logTitle() {
       if (this.logBranch && this.logInfo) {
         if (this.searchLogKeyword != "") {
           return this.logBranch + "(" + this.logInfo.length + ") [ Search '" + this.searchLogKeyword + "' " + (this.searchLogIndex + 1) + "/" + this.searchLogMatchNumber + " ]";
         } else {
           return this.logBranch + "(" + this.logInfo.length + ")";
         }
       } else {
         return "";
       }
     },

     compareLogTitle() {
       if (this.compareLogBranch && this.compareLogInfo) {
         return this.compareLogBranch + "(" + this.compareLogInfo.length + ")";
       } else {
         return "";
       }
     },
   },
   mounted() {
     var that = this;

     this.$root.$on("js_log_view_diff", function () {
       that.logViewDiff();
     });

     this.$root.$on("js_log_revert_commit", function () {
       that.logRevertCommit();
     });

     this.$root.$on("js_log_reset_last", function () {
       that.logResetLast();
     });

     this.$root.$on("js_log_reset_to", function () {
       that.logResetTo();
     });

     this.$root.$on("js_log_cherry_pick", function () {
       that.logCherryPick();
     });

     this.$root.$on("js_log_select_pg_up", function () {
       that.logSelectPgUp();
     });

     this.$root.$on("js_log_select_pg_dn", function () {
       that.logSelectPgDn();
     });

   },
   beforeDestroy() {
     this.$root.$off("js_log_view_diff");
     this.$root.$off("js_log_revert_commit");
     this.$root.$off("js_log_reset_last");
     this.$root.$off("js_log_reset_to");
     this.$root.$off("js_log_select_pg_up");
     this.$root.$off("js_log_select_pg_dn");
   },
   methods: {
     logViewDiff() {
       this.pyobject.show_commit_diff(this.logInfo[this.currentLogIndex].id);
     },

     logRevertCommit() {
       this.pyobject.log_revert_commit(this.logInfo[this.currentLogIndex].id);
     },

     logResetLast() {
       this.pyobject.log_reset_last(this.logInfo[0].id, this.logInfo[0].message);
     },

     logResetTo() {
       this.pyobject.log_reset_last(this.logInfo[this.currentLogIndex].id, this.logInfo[this.currentLogIndex].message);
     },

     logSelectPgUp() {
       this.$emit("updateLogIndex", this.currentLogIndex - getListPageElementNumber(this.$refs.loglist));
     },

     logSelectPgDn() {
       this.$emit("updateLogIndex", this.currentLogIndex + getListPageElementNumber(this.$refs.loglist));
     },

     logCherryPick() {
       var pickList = this.logInfo.filter(info => { return info.marked == "marked" });
       if (pickList.length == 0) {
         pickList.push(this.logInfo[this.currentLogIndex]);
       }

       this.pyobject.log_cherry_pick(pickList);
     },
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .log-box {
   width: 100%;
   height: 100%;

   display: flex;
   flex-direction: row;
 }

 .log-item {
   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;
   height: 30px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .log-id {
   width: 80px;
 }

 .log-date {
   padding-left: 20px;
   width: 150px;
 }

 .log-author {
   padding-left: 20px;
   width: 150px;

   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
 }

 .log-message {
   padding-left: 20px;
   flex: 1;

   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;

   width: 100px;
 }

 .highlight-line {
   width: 100%;
   z-index: 10;
   position: fixed;
 }

 .flex-expand {
   flex: 1;
 }

 .list {
   z-index: 100;
   max-height: calc(100vh - 150px);
   overflow-y: scroll;
 }

 .compare-log-list {
   width: 30%;
 }
</style>
