<template>
  <div class="log-box">
    <Dialog 
      class="flex-expand"
      :title="logTitle"
      hasScrollChild="true">
      <div
        class="list"
        ref="logs">
        <div
          v-for="info in logInfo"
          :key="info.index"
          class="log-item">
          <div class="log-id">
            {{ info.id.slice(0, 7) }}
          </div>
          <div class="log-date">
            {{ info.time }}
          </div>
          <div class="log-author">
            {{ info.author }}
          </div>
          <div class="log-message">
            {{ info.message }}
          </div>
        </div>
      </div>
    </Dialog>
    
    <Dialog 
      v-if="compareLogInfo.length > 0"
      class="compare-log-list"
      :title="compareLogTitle"
      hasScrollChild="true">
      <div class="list">
        <div
          v-for="info in compareLogInfo"
          :key="info.index"
          class="log-item">
          <div class="log-id">
            {{ info.id.slice(0, 7) }}
          </div>
          <div class="log-message">
            {{ info.message }}
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"

 export default {
   name: 'Log',
   components: {
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
     searchLogMatchIndex: Number,
     searchLogKeyword: String,
     searchLogMatchNumber: Number,
     searchLogIndex: Number,
     pyobject: Object
   },
   data() {
     return {
       currentPageElementNum: 0
     }
   },
   watch: {
     currentLogIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           this.updateItemBackground(oldVal, val);
           this.keepSelectVisible();
         }
       }
     },
     searchLogMatchIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           this.updateItemMatchColor(oldVal, val);
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

     this.showHighlightLine();
     this.refreshSceenElementNumber();

     this.$root.$on("logViewDiff", function () {
       that.logViewDiff();
     });

     this.$root.$on("logShowCompareBranch", function () {
       that.pyobject.log_show_compare_branch();
     });

     this.$root.$on("logHideCompareBranch", function () {
       that.pyobject.log_hide_compare_branch();
     });

     this.$root.$on("logRevertCommit", function () {
       that.logRevertCommit();
     });

     this.$root.$on("logResetLast", function () {
       that.logResetLast();
     });

     this.$root.$on("logResetTo", function () {
       that.logResetTo();
     });

     this.$root.$on("logCherryPick", function () {
       that.logCherryPick();
     });
     
     this.$root.$on("logRebaseBranch", function () {
       that.logRebaseBranch();
     });

     this.$root.$on("logSelectPgUp", function () {
       that.logSelectPgUp();
     });

     this.$root.$on("logSelectPgDn", function () {
       that.logSelectPgDn();
     });

     this.$root.$on("logMarkItem", function (index) {
       that.logMarkItem(index);
     });

     this.$root.$on("logUnmarkItem", function (index) {
       that.logUnmarkItem(index);
     });

     this.$root.$on("logUnmarkAllItem", function () {
       that.logUnmarkAllItem();
     });
   },
   beforeDestroy() {
     this.$root.$off("logViewDiff");
     this.$root.$off("logRevertCommit");
     this.$root.$off("logResetLast");
     this.$root.$off("logResetTo");
     this.$root.$off("logRebaseBranch");
     this.$root.$off("logSelectPgUp");
     this.$root.$off("logSelectPgDn");
     this.$root.$off("logMarkItem");
     this.$root.$off("logUnmarkItem");
     this.$root.$off("logUnmarkAllItem");
   },
   methods: {
     showHighlightLine() {
       if (this.currentLogIndex !== null && this.currentLogIndex >= 0) {
         this.$refs.logs.children[this.currentLogIndex].style.background = this.selectColor;
       }

       this.keepSelectVisible();
     },

     updateItemBackground(oldIndex, newIndex) {
       if (oldIndex !== null && oldIndex >= 0) {
         var oldItem = this.$refs.logs.children[oldIndex];
         oldItem.style.background = this.backgroundColor;
       }

       if (newIndex !== null && newIndex >= 0) {
         var newItem = this.$refs.logs.children[newIndex];
         newItem.style.background = this.selectColor;
       }
     },

     updateItemMatchColor(oldIndex, newIndex) {
       if (oldIndex !== null && oldIndex >= 0) {
         var oldItem = this.$refs.logs.children[oldIndex];
         oldItem.style.color = "";
       }

       if (newIndex !== null && newIndex >= 0) {
         var newItem = this.$refs.logs.children[newIndex];
         newItem.style.color = this.matchColor;
       }
     },
     
     logMarkItem(index) {
       this.$refs.logs.children[index].style.color = this.markColor;
     },

     logUnmarkItem(index) {
       this.$refs.logs.children[index].style.color = "";
     },

     logUnmarkAllItem() {
       for (var i=0; i < this.$refs.logs.children.length; i++) {
         this.$refs.logs.children[i].style.color = "";
       }
     },
     
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

     logRebaseBranch() {
       this.pyobject.log_rebase_branch();
     },

     logSelectPgUp() {
       this.refreshSceenElementNumber()
       this.$emit("updateLogIndex", this.currentLogIndex - this.currentPageElementNum);
     },

     logSelectPgDn() {
       this.refreshSceenElementNumber()
       this.$emit("updateLogIndex", this.currentLogIndex + this.currentPageElementNum);
     },

     refreshSceenElementNumber() {
       this.$nextTick(() => {
         var logList = this.$refs.logs
         var selectLog = this.$refs.logs.children[this.currentLogIndex]
         if (logList !== undefined && selectLog !== undefined) {
           this.currentPageElementNum = Math.floor(logList.clientHeight / selectLog.clientHeight);
         }
       });
     },
     
     logCherryPick() {
       var pickList = this.logInfo.filter(info => { return info.marked == "marked" });
       if (pickList.length == 0) {
         pickList.push(this.logInfo[this.currentLogIndex]);
       }
       
       this.pyobject.log_cherry_pick(pickList);
     },
     
     keepSelectVisible() {
       /* Use nextTick wait DOM update, then make sure current file in visible area. */
       this.$nextTick(function() {
         var selectLog = this.$refs.logs.children[this.currentLogIndex]
         if (selectLog !== undefined) {
           selectLog.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
         }
       })
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
