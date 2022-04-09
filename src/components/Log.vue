<template>
  <div class="log-box">
    <Dialog 
      class="flex-expand"
      :title="logBranch"
      hasScrollChild="true">
      <div
        class="list"
        ref="logs">
        <div
          v-for="info in logInfo"
          :key="info.index"
          class="log-item">
          <div
            class="log-id"
            :style="{ 'color': idColor }">
            {{ info.id.slice(0, 7) }}
          </div>
          <div
            class="log-date"
            :style="{ 'color': dateColor }">
            {{ info.time }}
          </div>
          <div
            class="log-author"
            :style="{ 'color': authorColor }">
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
      :title="compareLogBranch"
      hasScrollChild="true">
      <div class="list">
        <div
          v-for="info in compareLogInfo"
          :key="info.index"
          class="log-item">
          <div
            class="log-id"
            :style="{ 'color': idColor }">
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
     currentLogIndex: Number,
     pyobject: Object
   },
   data() {
     return {
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
   },
   mounted() {
     var that = this;

     this.showHighlightLine();

     this.$root.$on("logViewDiff", function () {
       that.logViewDiff();
     });

     this.$root.$on("logSearchForward", function () {
       that.pyobject.log_search_forward();
     });

     this.$root.$on("logSearchBackward", function () {
       that.pyobject.log_search_backward();
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
   },
   beforeDestroy() {
     this.$root.$off("logViewDiff");
     this.$root.$off("logSearchForward");
     this.$root.$off("logSearchBackward");
     this.$root.$off("logRevertCommit");
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

     logViewDiff() {
       this.pyobject.show_commit_diff(this.logInfo[this.currentLogIndex].id);
     },

     logRevertCommit() {
       this.pyobject.revert_commit(this.logInfo[this.currentLogIndex].id);
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
</style>
