<template>
  <div class="box">
    <div
      class="list"
      ref="logs">
      <div
        v-for="info in logInfo"
        :key="info.index"
        class="log-item"
        :style="{ 'height': lineHeight }">
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
  </div>
</template>

<script>
 export default {
   name: 'Log',
   props: {
     logInfo: Array,
     idColor: String,
     dateColor: String,
     authorColor: String,
     backgroundColor: String,
     selectColor: String,
     pyobject: Object
   },
   data() {
     return {
       lineHeight: "30px",
       currentCommitIndex: 0,
       currentCommitId: ""
     }
   },
   watch: {
     currentCommitIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           this.currentCommitId = this.logInfo[val].id;
           this.updateItemBackground(oldVal, val);
         }
       }
     },
   },
   mounted() {
     var that = this;

     this.currentCommitIndex = 0;
     this.updateItemBackground(null, 0);

     this.$root.$on("logSelectNext", function () {
       that.logSelectNext();
     });

     this.$root.$on("logSelectPrev", function () {
       that.logSelectPrev();
     });

     this.$root.$on("logSelectLast", function () {
       that.logSelectLast();
     });

     this.$root.$on("logSelectFirst", function () {
       that.logSelectFirst();
     });

     this.$root.$on("logViewDiff", function () {
       that.pyobject.show_commit_diff(that.currentCommitId, that.logInfo[that.currentCommitIndex + 1].id);
     });
   },
   beforeDestroy() {
     this.$root.$off("logSelectNext");
     this.$root.$off("logSelectPrev");
     this.$root.$off("logSelectLast");
     this.$root.$off("logSelectFirst");
     this.$root.$off("logViewDiff");
   },
   methods: {
     logSelectNext() {
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex++;
         this.keepSelectVisible();
       }
     },

     logSelectLast() {
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex = this.logInfo.length - 1;
         this.keepSelectVisible();
       }
     },

     logSelectPrev() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex--;
         this.keepSelectVisible();
       }
     },

     logSelectFirst() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex = 0;
         this.keepSelectVisible();
       }
     },

     updateItemBackground(oldIndex, newIndex) {
       if (oldIndex !== null) {
         var oldItem = this.$refs.logs.children[oldIndex];
         oldItem.style.background = this.backgroundColor;
       }
       
       if (newIndex !== null) {
         var newItem = this.$refs.logs.children[newIndex];
         newItem.style.background = this.selectColor;
       }
     },

     keepSelectVisible() {
       /* Use nextTick wait DOM update, then make sure current file in visible area. */
       this.$nextTick(function() {
         var selectLog = this.$refs.logs.children[this.currentCommitIndex]
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
 .box {
   width: 100%;
   height: 100%;
 }

 .log-item {
   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .log-id {
   width: 80px;
 }

 .log-date {
   padding-left: 20px;
   width: 200px;
 }

 .log-author {
   padding-left: 20px;
   width: 15%;

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

 .list {
   z-index: 100;
   max-height: calc(100vh - 100px);
   overflow-y: scroll;
 }
</style>
