<template>
  <div class="box">
    <div
      v-if="noFileSubmit()"
      class="clean-workspace">
      No file need submitted, clean workspace.
    </div>
    <div
      v-else
      class="diff-area">
      <div class="diff-file">
        <div v-if="unstageFileNumber() > 0">
          <div
            class="unstaged-title"
            :style="{ 'background': unstageTitleBackground() }">
            Unstaged changes ({{ unstageStatusInfo.length }})
          </div>
          <div
            v-for="(info, index) in unstageStatusInfo"
            :key="info"
            class="item"
            :style="{ 'background': unstageItemBackground(index) }">
            <div class="type">
              {{ info.type }}
            </div>
            <div class="file">
              {{ info.file }}
            </div>
          </div>
        </div>

        <div v-if="stageFileNumber() > 0">
          <div
            class="staged-title"
            :style="{ 'background': stageTitleBackground() }">
            Staged changes ({{ stageStatusInfo.length }})
          </div>
          <div
            v-for="(info, index) in stageStatusInfo"
            :key="info"
            class="item"
            :style="{ 'background': stageItemBackground(index) }">
            <div class="type">
              {{ info.type }}
            </div>
            <div class="file">
              {{ info.file }}
            </div>
          </div>
        </div>
      </div>
      <div class="diff-preview">
        <div v-html="prettyHtml"/>
      </div>
    </div>
  </div>
</template>

<script>
 var AU = require('ansi_up');
 var ansiUp = new AU.default;

 export default {
   name: 'Dashboard',
   props: {
     stageStatusInfo: Array,
     unstageStatusInfo: Array,
     backgroundColor: String,
     selectColor: String,
     pyobject: Object
   },
   data() {
     return {
       diffs: "",
       selectItemType: "",
       selectItemIndex: -1
     }
   },
   computed: {
     prettyHtml() {
       return ansiUp.ansi_to_html(this.diffs);
     },
   },
   mounted() {
     window.updateChangeDiff = this.updateChangeDiff;

     var that = this;

     if (this.unstageStatusInfo) {
       this.selectItemType = "unstage";
       this.selectItemIndex = -1;
     } else if (this.stageStatusInfo) {
       this.selectItemType = "stage";
       this.selectItemIndex = -1;
     }

     setTimeout(this.updateDiff, 1000)

     this.$root.$on("selectNextChangeItem", function () {
       that.selectNextChangeItem();
     });

     this.$root.$on("selectPrevChangeItem", function () {
       that.selectPrevChangeItem();
     });
   },
   beforeDestroy() {
     this.$root.$off("selectNextChangeItem");
     this.$root.$off("selectPrevChangeItem");
   },
   methods: {
     noFileSubmit() {
       return this.unstageFileNumber() + this.stageFileNumber() === 0;
     },

     unstageFileNumber() {
       var unstage_files_number = 0;
       if (this.unstageStatusInfo) {
         unstage_files_number = this.unstageStatusInfo.length;
       }

       return unstage_files_number;
     },

     stageFileNumber() {
       var stage_files_number = 0;
       if (this.stageStatusInfo) {
         stage_files_number = this.stageStatusInfo.length;
       }

       return stage_files_number;
     },

     updateDiff() {
       if (this.selectItemIndex === -1) {
         this.pyobject.update_diff(this.selectItemType, "");
       } else {
         if (this.selectItemType === "unstage") {
           this.pyobject.update_diff(this.selectItemType, this.unstageStatusInfo[this.selectItemIndex].file);
         } else {
           this.pyobject.update_diff(this.selectItemType, this.stageStatusInfo[this.selectItemIndex].file);
         }
       }
     },

     updateChangeDiff(diffString) {
       this.diffs = diffString;
     },

     selectNextChangeItem() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       if (this.selectItemType == "unstage") {
         if (this.selectItemIndex < this.unstageStatusInfo.length - 1) {
           this.selectItemIndex += 1;
         } else if (this.stageStatusInfo.length > 0) {
           this.selectItemType = "stage";
           this.selectItemIndex = -1;
         }
       } else if (this.selectItemType == "stage") {
         if (this.selectItemIndex == -1) {
           this.selectItemIndex = 0;
         } else if (this.selectItemIndex < this.stageStatusInfo.length - 1) {
           this.selectItemIndex += 1;
         }
       }

       if (oldSelectItemType != this.selectItemType ||
           oldSelectItemIndex != this.selectItemIndex) {
         this.updateDiff();
       }
     },

     selectPrevChangeItem() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       if (this.selectItemType == "stage") {
         if (this.selectItemIndex > 0) {
           this.selectItemIndex -= 1;
         } else if (this.selectItemIndex == 0) {
           this.selectItemIndex = -1;
         } else {
           this.selectItemType = "unstage";
           this.selectItemIndex = this.unstageStatusInfo.length - 1;
         }
       } else if (this.selectItemType == "unstage") {
         if (this.selectItemIndex > 0) {
           this.selectItemIndex -= 1;
         } else if (this.selectItemIndex == 0) {
           this.selectItemIndex = -1;
         }
       }

       if (oldSelectItemType != this.selectItemType ||
           oldSelectItemIndex != this.selectItemIndex) {
         this.updateDiff();
       }
     },

     unstageTitleBackground() {
       if (this.selectItemType === "unstage" && this.selectItemIndex === -1) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
       }
     },

     stageTitleBackground() {
       if (this.selectItemType === "stage" && this.selectItemIndex === -1) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
       }
     },

     unstageItemBackground(index) {
       if (this.selectItemType === "unstage" && this.selectItemIndex === index) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
       }
     },

     stageItemBackground(index) {
       if (this.selectItemType === "stage" && this.selectItemIndex === index) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
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

 .item {
   padding-left: 20px;
   padding-right: 10px;
   padding-top: 5px;
   padding-bottom: 5px;
   font-size: 16px;

   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .type {
   padding-right: 10px;
 }

 .clean-workspace {
   padding-left: 10px;
 }

 .unstaged-title {
   padding-top: 5px;
   padding-bottom: 5px;

   font-weight: bold;
   padding-left: 10px;
   margin-bottom: 5px;
   font-size: 16px;
 }

 .staged-title {
   padding-top: 5px;
   padding-bottom: 5px;

   font-weight: bold;
   padding-left: 10px;
   margin-top: 20px;
   margin-bottom: 5px;
   font-size: 16px;
 }

 .diff-area {
   display: flex;
   flex-direction: row;
   width: 100%;
   height: 100%;
 }

 .diff-file {
   width: 30%;
   height: 100%;
 }

 .diff-preview {
   width: 70%;
   height: 100%;
   padding-left: 10px;
   padding-right: 10px;

   white-space: pre-wrap;
   font-size: 16px;
 }
</style>
