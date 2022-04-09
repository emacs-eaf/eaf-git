<template>
  <div class="box">
    <Dialog
      v-if="noFileSubmit"
      title="Welcome">
      <div class="clean-workspace">
        No file need submitted, clean workspace.
      </div>
    </Dialog>
    <div
      v-else
      class="status-area">
      <div class="status-left-panel">
        <Dialog
          class="flex-expand"
          title="Commit">
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
        </Dialog>

        <Dialog
          v-if="stashInfo != ''"
          title="Stash"
          class="stash-dialog">
          <div class="stash-info-area">
            <div
              class="stash-item"
              v-for="info in stashInfo"
              :key="info.index">
              <div
                class="stash-id"
                :style="{ 'color': idColor }">
                {{ info.id.slice(0, 7) }}
              </div>
              <div
                class="stash-index"
                :style="{ 'color': indexColor }">
                stash@[{{ info.index }}]
              </div>
              <div class="stash-message">
                {{ info.message }}
              </div>
            </div>
          </div>
        </Dialog>

        <Dialog
          v-if="unpushInfo != ''"
          title="Unpush"
          class="unpush-dialog">
          <div class="unpush-info-area">
            {{ unpushInfo }}
          </div>
        </Dialog>
      </div>

      <Dialog
        class="flex-expand"
        title="Preview"
        hasScrollChild="true">
        <div
          class="status-preview-area"
          v-html="prettyHtml">
        </div>
      </Dialog>
    </div>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"

 var AU = require('ansi_up');
 var ansiUp = new AU.default;

 export default {
   name: 'Dashboard',
   components: {
     Dialog
   },
   props: {
     selectItemType: String,
     selectItemIndex: Number,
     stageStatusInfo: Array,
     unstageStatusInfo: Array,
     untrackStatusInfo: Array,
     unpushInfo: String,
     stashInfo: Array,
     diffs: String,
     backgroundColor: String,
     selectColor: String,
     indexColor: String,
     idColor: String,
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
   computed: {
     prettyHtml() {
       return ansiUp.ansi_to_html(this.diffs);
     },

     noFileSubmit() {
       return this.unstageFileNumber() + this.stageFileNumber() + this.untrackFileNumber() + this.stashInfo.length === 0 && this.unpushInfo === "";
     }
   },
   mounted() {

     var that = this;

     this.$root.$on("statusCopyChangeFilesToMirrorRepo", function () {
       window.pyobject.copy_change_files_to_mirror_repo();
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

     this.$root.$on("statusStashPush", function () {
       that.pyobject.status_stash_push();
     });
   },
   beforeDestroy() {
     this.$root.$off("statusCopyChangeFilesToMirrorRepo");
     this.$root.$off("statusStageFile");
     this.$root.$off("statusDeleteFile");
     this.$root.$off("statusCommitStage");
     this.$root.$off("statusCommitAll");
     this.$root.$off("statusCommitAndPush");
     this.$root.$off("statusPull");
     this.$root.$off("statusPush");
     this.$root.$off("statusCheckoutAll");
     this.$root.$off("statusStashPush");
   },
   methods: {
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

 .stash-info-area {
   padding: 20px;
   padding: 20px;
 }

 .stash-item {
   display: flex;
   flex-direction: row;
   align-items: center;
 }

 .stash-index {
   padding-left: 10px;
 }

 .stash-message {
   padding-left: 10px;
 }

 .status-preview-area {
   height: 100%;
   padding-left: 10px;
   padding-right: 10px;

   white-space: pre-wrap;
   font-size: 16px;
   
   max-height: calc(100vh - 150px);
   
   overflow-y: scroll;
 }

 .split-line {
   height: 20px;
 }
 
 .stash-dialog {
   max-height: 30%;
 }

 .unpush-dialog {
   max-height: 30%;
 }
</style>
