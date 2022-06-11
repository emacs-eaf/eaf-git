<template>
  <div
    :class="[ logboxClass ]"
    class="log-box">
    <Dialog
      class="local-log"
      :backgroundColor="backgroundColor"
      :title="logTitle">
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
      :backgroundColor="backgroundColor"
      class="compare-log-list"
      :title="compareLogTitle">
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
 
 import { Layout, keepSelectVisible, getListPageElementNumber } from "./utils.js"

 export default {
   name: 'Log',
   components: {
     'virtual-list': VirtualList,
     Dialog
   },
   props: {
     layout: String,
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

     logboxClass() {
       return this.layout === Layout.Vertical ? "log-box-vertical" : "log-box-horizontal";
     }
   },
   mounted() {
     var that = this;
     
     this.$root.$on("log_view_diff", function () {
       that.logViewDiff();
     });

     this.$root.$on("log_revert_commit", function () {
       that.logRevertCommit();
     });

     this.$root.$on("log_revert_to", function () {
       that.logRevertTo();
     });
     
     this.$root.$on("log_reset_last", function () {
       that.logResetLast();
     });

     this.$root.$on("log_reset_to", function () {
       that.logResetTo();
     });

     this.$root.$on("log_cherry_pick", function () {
       that.logCherryPick();
     });

     this.$root.$on("log_copy_commit_id", function () {
       that.logCopyCommitID();
     });

     this.$root.$on("log_copy_commit_url", function () {
       that.logCopyCommitUrl();
     });

     this.$root.$on("log_select_pg_up", function () {
       that.logSelectPgUp();
     });

     this.$root.$on("log_select_pg_dn", function () {
       that.logSelectPgDn();
     });

   },
   beforeDestroy() {
     this.$root.$off("log_view_diff");
     this.$root.$off("log_revert_commit");
     this.$root.$off("log_revert_to");
     this.$root.$off("log_reset_last");
     this.$root.$off("log_reset_to");
     this.$root.$off("log_cherry_pick");
     this.$root.$off("log_copy_commit_id");
     this.$root.$off("log_copy_commit_url");
     this.$root.$off("log_select_pg_up");
     this.$root.$off("log_select_pg_dn");
   },
   methods: {
     logViewDiff() {
       this.pyobject.show_commit_diff(this.logInfo[this.currentLogIndex].id);
     },

     logRevertCommit() {
       this.pyobject.log_revert_commit(this.logInfo[this.currentLogIndex].id);
     },

     logRevertTo() {
       this.pyobject.log_revert_to(this.logInfo[this.currentLogIndex].id);
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

     logCopyCommitID() {
       const that = this;
       const commitId = this.logInfo[this.currentLogIndex].id;
       navigator.clipboard.writeText(commitId).then(() => {
         that.pyobject.send_message_to_emacs(`Copied ${commitId} successfully.`);
       }, () => {
         that.pyobject.send_message_to_emacs(`Copy ${commitId} failed.`);
       });
     },
     
     logCopyCommitUrl() {
       this.pyobject.copy_commit_url(this.logInfo[this.currentLogIndex].id);
     }
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .log-box {
   width: 100%;
   height: 100%;

   display: flex;
 }

 .log-box-horizontal {
   flex-direction: row;
 }

 .log-box-vertical {
   flex-direction: column;
 }

 .local-log {
   /* 70% */
   flex-grow: 7;
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
   overflow-y: scroll;
   height: 100%
 }

 .compare-log-list {
   /* 30% */
   flex-grow: 3;
 }
</style>
