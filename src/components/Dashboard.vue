<template>
  <div class="box">
    <Dialog
      v-if="isCleanWorkspace"
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
          title="Status">
          <div
            v-if="noFileChanged"
            class="changed-count">
            {{ changedCount }}
          </div>
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
              <div
                :style="{ 'color': idColor }"
                class="count">
                <div class="add">
                  +{{ info.add_count }}
                </div>
                <div class="delete">
                  -{{ info.delete_count }}
                </div>
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
              <div
                :style="{ 'color': idColor }"
                class="count">
                <div class="add">
                  +{{ info.add_count }}
                </div>
                <div class="delete">
                  -{{ info.delete_count }}
                </div>
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
              <div
                :style="{ 'color': idColor }"
                class="count">
                <div class="add">
                  +{{ info.add_count }}
                </div>
                <div class="delete">
                  -{{ info.delete_count }}
                </div>
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
          v-if="unpushInfo.length > 0"
          title="Unpush"
          class="unpush-dialog">
          <div 
            v-for="info in unpushInfo"
            :key="info"
            class="unpush-info-item">
            {{ info }}
          </div>
        </Dialog>
      </div>

      <div class="status-right-panel">
        <Dialog
          v-if="patchSetNumber() > 0"
          title="Preview"
          hasScrollchild="true">
          <div
            ref="scrollArea"
            class="hunks-preview-area">
            <div
              ref="patchSets"
              v-for="(patch, pIndex) in patchSet"
              :key="patch.path">
              <strong> {{ patch.patch_info }} </strong>
              <div
                v-for="(hunk, hIndex) in patch.diff_hunks"
                :key="hunk"
                class="hunk"
                :style="{ 'background': selectHunkBackgroud(pIndex, hIndex) }"
                v-html="hunk">
              </div>
            </div>
        </Dialog>
        <Dialog
          v-else
          title="Preview"
          hasScrollChild="true">
          <div
            ref="scrollArea"
            class="status-preview-area"
            v-html="prettyHtml">
          </div>
        </Dialog>
          </div>
      </div>
    </div>
</template>

<script>
 import Dialog from "./Dialog.vue"

 export default {
   name: 'Dashboard',
   components: {
     Dialog
   },
   props: {
     selectItemType: String,
     selectItemIndex: Number,
     selectPatchIndex: Number,
     selectHunkIndex: Number,
     stageStatusInfo: Array,
     unstageStatusInfo: Array,
     untrackStatusInfo: Array,
     unpushInfo: String,
     stashInfo: Array,
     diffs: String,
     patchSet: Array,
     diffsType: String,
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
     selectHunkIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         this.keepHunkVisible();
       },
       deep: true
     },
   },
   computed: {
     prettyHtml() {
       return this.diffs;
     },

     isCleanWorkspace() {
       return this.unstageFileNumber() + this.stageFileNumber() + this.untrackFileNumber() + this.stashInfo.length === 0 && this.unpushInfo.length === 0;
     },

     noFileChanged() {
       return this.unstageFileNumber() + this.stageFileNumber() + this.untrackFileNumber() !== 0;
     },

     changedCount() {
       var fileChangedNumber = this.unstageFileNumber() + this.stageFileNumber() + this.untrackFileNumber();
       var addCount = 0;
       var deleteCount = 0;

       if (this.unstageStatusInfo && this.unstageStatusInfo.length > 0) {
         addCount += this.unstageStatusInfo.map(info => info.add_count).reduce((x, y) => x + y);
         deleteCount += this.unstageStatusInfo.map(info => info.delete_count).reduce((x, y) => x + y);
       }
       if (this.stageStatusInfo && this.stageStatusInfo.length > 0) {
         addCount += this.stageStatusInfo.map(info => info.add_count).reduce((x, y) => x + y);
         deleteCount += this.stageStatusInfo.map(info => info.delete_count).reduce((x, y) => x + y);
       }
       if (this.untrackStatusInfo && this.untrackStatusInfo.length > 0) {
         addCount += this.untrackStatusInfo.map(info => info.add_count).reduce((x, y) => x + y);
         deleteCount += this.untrackStatusInfo.map(info => info.delete_count).reduce((x, y) => x + y);
       }

       return fileChangedNumber + " files changed, " + addCount + " insertions, " + deleteCount + " deletions";
     }
   },
   mounted() {

     var that = this;

     this.$root.$on("status_stage_hunk", function() {
       that.pyobject.status_stage_hunk(that.selectItemType, that.selectPatchIndex, that.selectHunkIndex);
     });

     this.$root.$on("status_stage_file", function () {
       that.pyobject.status_stage_file(that.selectItemType, that.selectItemIndex);
     });

     this.$root.$on("status_delete_file", function () {
       that.pyobject.status_delete_file(that.selectItemType, that.selectItemIndex);
     });

     this.$root.$on("status_preview_scroll_up_line", function () {
       that.statusPreviewScrollUpLine();
     });

     this.$root.$on("status_preview_scroll_down_line", function () {
       that.statusPreviewScrollDownLine();
     });

     this.$root.$on("status_preview_scroll_up", function () {
       that.statusPreviewScrollUp();
     });

     this.$root.$on("status_preview_scroll_down", function () {
       that.statusPreviewScrollDown();
     });
   },
   beforeDestroy() {
     this.$root.$off("js_status_stage_hunk");
     this.$root.$off("js_status_stage_file");
     this.$root.$off("js_status_delete_file");
     this.$root.$off("js_status_preview_scroll_down");
     this.$root.$off("js_status_preview_scroll_up");
     this.$root.$off("js_status_preview_scroll_up_line");
     this.$root.$off("js_status_preview_scroll_down_line");
   },
   methods: {
     patchSetNumber() {
       return this.patchSet ? this.patchSet.length : 0;
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

     selectHunkBackgroud(patchIndex, hunkIndex) {
       if (this.selectPatchIndex === patchIndex && this.selectHunkIndex == hunkIndex) {
         return this.selectColor;
       } else {
         return this.backgroundColor;
       }
     },

     keepHunkVisible() {
       this.$nextTick(function() {
         var selectPatch = this.$refs.patchSets[this.selectPatchIndex];

         if (selectPatch != undefined) {
           /* First child of patchSet is patch.patch_info, need add 1 offset. */
           var selectHunk = selectPatch.children[this.selectHunkIndex + 1]; 
           
           if (selectHunk != undefined) {
             selectHunk.scrollIntoView();
             
             /* Scroll to top if select the first hunk. */
             if (this.selectPatchIndex === 0 && this.selectHunkIndex === 0) {
               this.$refs.scrollArea.scrollTop = 0;
             }
           }
         }
       })
     },

     statusPreviewScrollUp() {
       this.$refs.scrollArea.scrollTop = this.$refs.scrollArea.scrollTop + this.$refs.scrollArea.clientHeight;
     },

     statusPreviewScrollDown() {
       this.$refs.scrollArea.scrollTop = this.$refs.scrollArea.scrollTop - this.$refs.scrollArea.clientHeight;
     },

     statusPreviewScrollUpLine() {
       this.$refs.scrollArea.scrollTop = this.$refs.scrollArea.scrollTop + 50;
     },

     statusPreviewScrollDownLine() {
       this.$refs.scrollArea.scrollTop = this.$refs.scrollArea.scrollTop - 50;
     }
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

 .file {
   flex: 1;
 }

 .count {
   display: flex;
   flex-direction: row;
 }

 .delete {
   padding-left: 5px;
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

 .status-right-panel {
   width: 70%;
   max-height: calc(100vh - 110px);
   height: 100%;
 }

 .flex-expand {
   flex: 1;
 }

 .unpush-info-item {
   display: block;
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 3px;
   padding-bottom: 3px;
   
   width: 25vw;
   
   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
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

 .hunks-preview-area {
   overflow-y: scroll;
   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;
   height: 95%;
 }

 .status-preview-area {
   height: 100%;
   padding-left: 10px;
   padding-right: 10px;

   white-space: pre-wrap;
   font-size: 16px;

   overflow-y: scroll;

   display: flex;
 }

 .status-preview-area ::v-deep pre {
   width: 1;
 }

 .hunks-preview-area ::v-deep pre {
   width: 1;
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

 .changed-count {
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 10px;
   padding-bottom: 20px;
   font-weight: bold;
 }

 .hunk {
   padding: 10px;
   border-radius: 5px;
 }
</style>
