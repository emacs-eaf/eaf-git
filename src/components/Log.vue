<template>
  <div class="box">
    <div ref="logs">
      <div
        v-for="info in logInfo"
        :key="info.id"
        class="log-item"
        :style="{ 'background': itemBackgroundColor(info) }">
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
     currentCommitIndex: Number,
     currentCommitId: String,
     idColor: String,
     dateColor: String,
     authorColor: String,
     backgroundColor: String,
     selectColor: String
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
   mounted() {
     var that = this;

     this.$root.$on("selectNextLog", function () {
       that.selectNextLog();
     });

     this.$root.$on("selectPrevLog", function () {
       that.selectPrevLog();
     });

     this.$root.$on("viewLogDiff", function () {

     });
   },
   methods: {
     itemBackgroundColor(item) {
       if (item.id == this.currentCommitId) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
       }
     },

     selectNextLog() {
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex++;
         this.keepSelectVisible();
       }
     },

     selectPrevLog() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex--;
         this.keepSelectVisible();
       }
     },

     keepSelectVisible() {
       /* Use nextTick wait DOM update, then make sure current file in visible area. */
       this.$nextTick(function(){
         var selectLog = this.$refs.logs.children[this.currentCommitIndex]
         if (selectLog !== undefined) {
           selectLog.scrollIntoViewIfNeeded(false);
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
   padding-top: 2px;
   padding-bottom: 2px;
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
</style>
