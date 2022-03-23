<template>
  <div class="box">
    <div
      ref="highlight-line"
      class="highlight-line"
      :style="{ 'background': selectColor, 'height': lineHeight, 'top': lineTop }">
    </div>
    <div
      class="list"
      ref="logs">
      <div
        v-for="info in logInfo"
        :key="info.id"
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
       lineTop: 0,
       currentCommitIndex: 0,
       currentCommitId: ""
     }
   },
   watch: {
     currentCommitIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           this.currentCommitId = this.logInfo[this.currentCommitIndex].id;
         }
       }
     },
   },
   created () {
     window.addEventListener('scroll', this.handleScroll);
   },
   destroyed () {
     window.removeEventListener('scroll', this.handleScroll);
   },
   mounted() {
     var that = this;

     this.currentCommitIndex = 0;
     this.updateLineCoordinate();

     this.$root.$on("selectNextLog", function () {
       that.selectNextLog();
     });

     this.$root.$on("selectPrevLog", function () {
       that.selectPrevLog();
     });

     this.$root.$on("selectLastLog", function () {
       that.selectLastLog();
     });

     this.$root.$on("selectFirstLog", function () {
       that.selectFirstLog();
     });

     this.$root.$on("viewLogDiff", function () {
       that.pyobject.show_commit_diff(that.currentCommitId, that.logInfo[that.currentCommitIndex + 1].id);
     });
   },
   beforeDestroy() {
     this.$root.$off("selectNextLog");
     this.$root.$off("selectPrevLog");
     this.$root.$off("selectLastLog");
     this.$root.$off("selectFirstLog");
     this.$root.$off("viewLogDiff");
   },
   methods: {
     selectNextLog() {
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex++;
         this.updateLineCoordinate();
         this.keepSelectVisible();
       }
     },

     selectLastLog() {
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex = this.logInfo.length - 1;
         this.updateLineCoordinate();
         this.keepSelectVisible();
       }
     },

     selectPrevLog() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex--;
         this.updateLineCoordinate();
         this.keepSelectVisible();
       }
     },

     selectFirstLog() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex = 0;
         this.updateLineCoordinate();
         this.keepSelectVisible();
       }
     },

     updateLineCoordinate() {
       this.lineTop = this.$refs.logs.children[this.currentCommitIndex].getBoundingClientRect().top;
     },

     handleScroll() {
       this.updateLineCoordinate();
     },

     keepSelectVisible() {
       /* Use nextTick wait DOM update, then make sure current file in visible area. */
       this.$nextTick(function(){
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
 }
</style>
