<template>
  <div class="box">
    <div
      v-if="noFileSubmit"
      class="clean-workspace">
      <div>
        No file need submitted, clean workspace.
      </div>
    </div>
    <div
      v-else
      class="status-area">
      <div class="status-left-panel">
        <fieldset class="dialog flex-expand">
          <legend class="dialog-title">Commit</legend>
          <div v-if="untrackFileNumber() > 0">
            <div
              class="untrack-title"
              :style="{ 'background': untrackTitleBackground() }">
              Untrackd changes ({{ untrackStatusInfo.length }})
            </div>
            <div
              v-for="(info, index) in untrackStatusInfo"
              :key="info"
              class="item"
              :style="{ 'background': untrackItemBackground(index) }">
              <div class="type">
                {{ info.type }}
              </div>
              <div class="file">
                {{ info.file }}
              </div>
            </div>
            <div class="split-line"/>
          </div>

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
            <div class="split-line"/>
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
        </fieldset>

        <fieldset
          v-if="unpushInfo != ''"
          class="dialog">
          <legend class="dialog-title">Unpush</legend>
          <div class="unpush-info-area">
            {{ unpushInfo }}
          </div>
        </fieldset>
      </div>
      <fieldset class="dialog flex-expand">
        <legend class="dialog-title">Preview</legend>
        <div class="status-preview-area">
          <div
            class="preview-code"
            v-html="prettyHtml"/>
        </div>
      </fieldset>
    </div>
  </div>
</template>

<script>
 var AU = require('ansi_up');
 var ansiUp = new AU.default;

 export default {
   name: 'Dashboard',
   props: {
     backgroundColor: String,
     selectColor: String,
     pyobject: Object
   },
   watch: {
     stageStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         window.pyobject.vue_update_stage_status(val);
       },
       deep: true
     },
     unstageStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         window.pyobject.vue_update_unstage_status(val);
       },
       deep: true
     },
     untrackStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         window.pyobject.vue_update_untrack_status(val);
       },
       deep: true
     },
   },
   data() {
     return {
       diffs: "",
       selectItemType: "",
       selectItemIndex: -1,
       stageStatusInfo: [],
       unstageStatusInfo: [],
       untrackStatusInfo: [],
       unpushInfo: ""
     }
   },
   computed: {
     prettyHtml() {
       return ansiUp.ansi_to_html(this.diffs);
     },

     noFileSubmit() {
       return this.unstageFileNumber() + this.stageFileNumber() + this.untrackFileNumber() === 0 && this.unpushInfo === "";
     }
   },
   mounted() {
     window.updateChangeDiff = this.updateChangeDiff;
     window.updateStatusInfo = this.updateStatusInfo;
     window.updateSelectInfo = this.updateSelectInfo;
     window.updateUnpushInfo = this.updateUnpushInfo;

     var that = this;

     if (this.untrackStatusInfo) {
       this.selectItemType = "untrack";
       this.selectItemIndex = -1;
     } else if (this.unstageStatusInfo) {
       this.selectItemType = "unstage";
       this.selectItemIndex = -1;
     } else if (this.stageStatusInfo) {
       this.selectItemType = "stage";
       this.selectItemIndex = -1;
     }

     setTimeout(this.updateDiff, 1000)

     this.$root.$on("statusCopyChangeFilesToMirrorRepo", function () {
       window.pyobject.copy_change_files_to_mirror_repo();
     });
     
     this.$root.$on("statusSelectNext", function () {
       that.statusSelectNext();
     });

     this.$root.$on("statusSelectPrev", function () {
       that.statusSelectPrev();
     });

     this.$root.$on("statusStageFile", function () {
       that.pyobject.status_stage_file(that.selectItemType, that.selectItemIndex);
     });

     this.$root.$on("statusDeleteFile", function () {
       that.pyobject.status_delete_file(that.selectItemType, that.selectItemIndex);
     });

     this.$root.$on("statusCommitStage", function () {
       that.pyobject.status_commit_stage();
     });

     this.$root.$on("statusCommitAll", function () {
       that.pyobject.status_commit_all();
     });

     this.$root.$on("statusCommitAndPush", function () {
       that.pyobject.status_commit_and_push();
     });

     this.$root.$on("statusPull", function () {
       that.pyobject.status_pull();
     });

     this.$root.$on("statusPush", function () {
       that.pyobject.status_push();
     });

     this.$root.$on("statusCheckoutAll", function () {
       that.pyobject.status_checkout_all();
     });
   },
   beforeDestroy() {
     this.$root.$off("statusCopyChangeFilesToMirrorRepo");
     this.$root.$off("statusSelectNext");
     this.$root.$off("statusSelectPrev");
     this.$root.$off("statusStageFile");
     this.$root.$off("statusDeleteFile");
     this.$root.$off("statusCommitStage");
     this.$root.$off("statusCommitAll");
     this.$root.$off("statusCommitAndPush");
     this.$root.$off("statusPull");
     this.$root.$off("statusPush");
     this.$root.$off("statusCheckoutAll");
   },
   methods: {
     updateSelectInfo(stageStatusInfo, unstageStatusInfo, untrackStatusInfo, selectItemType, selectItemIndex) {
       this.stageStatusInfo = stageStatusInfo;
       this.unstageStatusInfo = unstageStatusInfo;
       this.untrackStatusInfo = untrackStatusInfo;
       this.selectItemIndex = selectItemIndex;
       this.selectItemType = selectItemType;
     },

     updateStatusInfo(stageStatusInfo, unstageStatusInfo, untrackStatusInfo) {
       this.stageStatusInfo = stageStatusInfo;
       this.unstageStatusInfo = unstageStatusInfo;
       this.untrackStatusInfo = untrackStatusInfo;
     },

     updateUnpushInfo(unpushInfo) {
       this.unpushInfo = unpushInfo["info"];
     },

     untrackFileNumber() {
       var untrack_files_number = 0;
       if (this.untrackStatusInfo) {
         untrack_files_number = this.untrackStatusInfo.length;
       }

       return untrack_files_number;
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
         if (this.selectItemType === "untrack") {
           this.pyobject.update_diff(this.selectItemType, this.untrackStatusInfo[this.selectItemIndex].file);
         } else if (this.selectItemType === "unstage") {
           this.pyobject.update_diff(this.selectItemType, this.unstageStatusInfo[this.selectItemIndex].file);
         } else {
           this.pyobject.update_diff(this.selectItemType, this.stageStatusInfo[this.selectItemIndex].file);
         }
       }
     },

     updateChangeDiff(diffString) {
       this.diffs = diffString;
     },

     statusSelectNext() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       if (this.selectItemType == "untrack") {
         if (this.selectItemIndex < this.untrackStatusInfo.length - 1) {
           this.selectItemIndex += 1;
         } else if (this.unstageStatusInfo.length > 0) {
           this.selectItemType = "unstage";
           this.selectItemIndex = -1;
         } else if (this.stageStatusInfo.length > 0) {
           this.selectItemType = "stage";
           this.selectItemIndex = -1;
         }
       } else if (this.selectItemType == "unstage") {
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

     statusSelectPrev() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       if (this.selectItemType == "stage") {
         if (this.selectItemIndex > 0) {
           this.selectItemIndex -= 1;
         } else if (this.selectItemIndex == 0) {
           this.selectItemIndex = -1;
         } else if (this.unstageStatusInfo.length > 0) {
           this.selectItemType = "unstage";
           this.selectItemIndex = this.unstageStatusInfo.length - 1;
         } else if (this.untrackStatusInfo.length > 0) {
           this.selectItemType = "untrack";
           this.selectItemIndex = this.untrackStatusInfo.length - 1;
         }
       } else if (this.selectItemType == "unstage") {
         if (this.selectItemIndex > 0) {
           this.selectItemIndex -= 1;
         } else if (this.selectItemIndex == 0) {
           this.selectItemIndex = -1;
         } else if (this.untrackStatusInfo.length > 0) {
           this.selectItemType = "untrack";
           this.selectItemIndex = this.untrackStatusInfo.length - 1;
         }
       } else if (this.selectItemType == "untrack") {
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

     untrackTitleBackground() {
       if (this.selectItemType === "untrack" && this.selectItemIndex === -1) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
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

     untrackItemBackground(index) {
       if (this.selectItemType === "untrack" && this.selectItemIndex === index) {
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
   display: flex;
   flex-direction: column;
   align-items: center;
   justify-content: center;
   font-size: 20px;
   height: 100%;
   width: 100%;
 }

 .untrack-title {
   padding-top: 5px;
   padding-bottom: 5px;

   font-weight: bold;
   padding-left: 10px;
   font-size: 16px;
 }

 .unstaged-title {
   padding-top: 5px;
   padding-bottom: 5px;

   font-weight: bold;
   padding-left: 10px;
   font-size: 16px;
 }

 .staged-title {
   padding-top: 5px;
   padding-bottom: 5px;

   font-weight: bold;
   padding-left: 10px;
   font-size: 16px;
 }

 .status-area {
   display: flex;
   flex-direction: row;
   width: 100%;
   height: 100%;
 }

 .status-left-panel {
   display: flex;
   flex-direction: column;

   width: 30%;
   height: 100%;
 }

 .flex-expand {
   flex: 1;
 }

 .unpush-info-area {
   padding: 20px;
   padding: 20px;
 }

 .status-preview-area {
   width: 70%;
   height: 100%;
   padding-left: 10px;
   padding-right: 10px;

   white-space: pre-wrap;
   font-size: 16px;
 }
 
 .preview-code {
   max-height: calc(100vh - 150px);
   overflow-y: scroll;
 }

 .split-line {
   height: 20px;
 }

 .dialog {
   border: 1px solid;
   border-radius: 5px;
   margin: 10px;
 }

 .dialog-title {
   margin-left: 1em;
   padding: 0.2em 0.8em
 }
</style>
