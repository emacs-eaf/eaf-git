<template>
  <div class="box">
    <Dialog
      v-if="isCleanWorkspace"
      :backgroundColor="backgroundColor"
      title="Welcome">
      <div class="clean-workspace">
        No file need submitted, clean workspace.
      </div>
    </Dialog>
    <div
      v-else
      :class="[ layoutClass ]"
      class="status-area">
      <div class="status-left-panel">
        <Dialog
          ref="statusDialog"
          :backgroundColor="isSelected('status', -1) ? selectColor : backgroundColor"
          class="files-dialog"
          :collapsed="isCollapsed('status')"
          :title="`Status (Untracked: ${untrackStatusInfo.length}, Unstaged: ${unstageStatusInfo.length}, Staged: ${stageStatusInfo.length})`">
          <div
            v-if="noFileChanged"
            class="changed-count">
            {{ changedCount }}
          </div>
          <div
            class="untrack-area collapsible-item collapsible"
            :class="{ collapsed: isCollapsed('untrack') }"
            ref="untracklist"
            v-if="untrackStatusNumber() > 0">
            <div
              ref="untrackTitle"
              class="untrack-title"
              :class="{ selected: isSelected('untrack', -1) }">
              Untracked changes ({{ untrackStatusInfo.length }})
            </div>
            <div
              v-for="(info, index) in untrackStatusInfo"
              :key="info"
              class="item collapsible-item"
              :class="{ selected: isSelected('untrack', index) }">
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

          <div
            class="collapsible-item collapsible"
            :class="{ collapsed: isCollapsed('unstage') }"
            v-if="unstageStatusNumber() > 0"
            ref="unstagelist">
            <div
              ref="unstageTitle"
              class="unstaged-title"
              :class="{ selected: isSelected('unstage', -1) }">
              Unstaged changes ({{ unstageStatusInfo.length }})
            </div>
            <div
              v-for="(info, index) in unstageStatusInfo"
              :key="info"
              class="item collapsible-item"
              :class="{ selected: isSelected('unstage', index) }">
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

          <div
            class="collapsible-item collapsible"
            :class="{ collapsed: isCollapsed('stage') }"
            v-if="stageStatusNumber() > 0"
            ref="stagelist">
            <div
              ref="stageTitle"
              class="staged-title"
              :class="{ selected: isSelected('stage', -1) }">
              Staged changes ({{ stageStatusInfo.length }})
            </div>
            <div
              v-for="(info, index) in stageStatusInfo"
              :key="info"
              class="item collapsible-item"
              :class="{ selected: isSelected('stage', index) }">
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
          v-if="stashStatusInfo != ''"
          ref="stashDialog"
          :backgroundColor="isSelected('stash', -1) ? selectColor : backgroundColor"
          :title="`Stashes (${stashStatusInfo.length})`"
          :collapsed="isCollapsed('stash')"
          class="stash-dialog">
          <div
            ref="stashlist"
            class="stash-info-area collapsible-item">
            <div
              class="stash-item"
              v-for="info in stashStatusInfo"
              :key="info.index"
              :class="{ selected: isSelected('stash', info.index) }">
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
          v-if="unpushStatusInfo.length > 0"
          ref="unpushDialog"
          :backgroundColor="isSelected('unpush', -1) ? selectColor : backgroundColor"
          :title="`Unpushed (${unpushStatusInfo.length})`"
          :collapsed="isCollapsed('unpush')"
          class="unpush-dialog">
          <div
            ref="unpushlist"
            class="unpush-info-area collapsible-item">
            <div
              v-for="(info, index) in unpushStatusInfo"
              :key="info"
              :class="{ selected: isSelected('unpush', index) }"
              class="unpush-info-item">
              {{ info }}
            </div>
          </div>
        </Dialog>
      </div>

      <div class="status-right-panel">
        <Dialog
          v-if="patchSetNumber() > 0"
          :backgroundColor="backgroundColor"
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
          </div>
        </Dialog>
        <Dialog
          v-else
          :backgroundColor="backgroundColor"
          title="Preview">
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
     layoutClass: String,

     selectItemType: String,
     selectItemIndex: Number,
     selectPatchIndex: Number,
     selectHunkIndex: Number,
     stageStatusInfo: Array,
     unstageStatusInfo: Array,
     untrackStatusInfo: Array,
     unpushStatusInfo: String,
     stashStatusInfo: Array,

     statusState: Object,

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
       return this.unstageStatusNumber() + this.stageStatusNumber() + this.untrackStatusNumber() + this.stashStatusNumber() + this.unpushStatusNumber() === 0;
     },

     noFileChanged() {
       return this.unstageStatusNumber() + this.stageStatusNumber() + this.untrackStatusNumber() !== 0;
     },

     changedCount() {
       var fileChangedNumber = this.unstageStatusNumber() + this.stageStatusNumber() + this.untrackStatusNumber();
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
     },
   },
   mounted() {

     var that = this;

     this.$root.$on("status_manage_hunk", function() {
       that.pyobject.status_manage_hunk(that.selectItemType, that.selectPatchIndex, that.selectHunkIndex);
     });

     this.$root.$on("status_delete_hunk", function() {
       that.pyobject.status_delete_hunk(that.selectItemType, that.selectPatchIndex, that.selectHunkIndex);
     })

     this.$root.$on("status_view_file", function () {
       that.pyobject.status_view_file(that.selectItemType, that.selectItemIndex);
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
     this.$root.$off("status_manage_hunk");
     this.$root.$off("status_delete_hunk");
     this.$root.$off("status_view_file");
     this.$root.$off("status_stage_file");
     this.$root.$off("status_delete_file");
     this.$root.$off("status_preview_scroll_down");
     this.$root.$off("status_preview_scroll_up");
     this.$root.$off("status_preview_scroll_up_line");
     this.$root.$off("status_preview_scroll_down_line");
   },
   methods: {
     patchSetNumber() {
       return this.patchSet ? this.patchSet.length : 0;
     },
     untrackStatusNumber() {
       var untrack_files_number = 0;
       if (this.untrackStatusInfo) {
         untrack_files_number = this.untrackStatusInfo.length;
       }

       return untrack_files_number;
     },

     unstageStatusNumber() {
       var unstage_files_number = 0;
       if (this.unstageStatusInfo) {
         unstage_files_number = this.unstageStatusInfo.length;
       }

       return unstage_files_number;
     },

     stageStatusNumber() {
       var stage_files_number = 0;
       if (this.stageStatusInfo) {
         stage_files_number = this.stageStatusInfo.length;
       }

       return stage_files_number;
     },

     stashStatusNumber() {
       var stash_files_number = 0;
       if (this.stashStatusInfo) {
         stash_files_number = this.stashStatusInfo.length;
       }

       return stash_files_number;
     },

     unpushStatusNumber() {
       var unpush_files_number = 0;
       if (this.unpushStatusInfo) {
         unpush_files_number = this.unpushStatusInfo.length;
       }

       return unpush_files_number;
     },

     /**
      * Whether the section with the specified type is collapsed or expanded
      */
     isCollapsed(type) {
       if (!this.statusState.dataRef) {
         return false;
       }

       let startIndex = this.statusState.dataRef[type].stateStartIndex;
       if (startIndex == -1) {
         return false
       }

       return this.statusState.states[startIndex].state === 'collapsed';
     },

     /**
      * whether the item with the specified type and index is currently selected or not
      */
     isSelected(type, index) {
       if (!this.statusState["states"]) {
         return false;
       }

       let dataRef = this.statusState.dataRef[type];
       if (dataRef.stateStartIndex < 0) {
         // not displayed
         return false;
       }

       let stateIndex = dataRef.stateStartIndex + index + 1;
       let state = this.statusState.states[stateIndex];
       let selected = state.selected;
       let dataIndex = state.dataIndex;

       if (selected) {
         // scroll into the view of the current selected item
         this.$nextTick(function() {
           let typeToRef = {
             status: {
               type: "dialog",
               parent: "statusDialog"
             },
             untrack: {
               parent: "untrackTitle",
               list: "untracklist"
             },
             unstage: {
               parent: "unstageTitle",
               list: "unstagelist"
             },
             stage: {
               parent: "stageTitle",
               list: "stagelist"
             },
             stash: {
               type: "dialog",
               parent: "stashDialog",
               list: "stashlist"
             },
             unpush: {
               type: "dialog",
               parent: "unpushDialog",
               list: "unpushlist"
             }
           };

           // get element reference and scroll to view
           let ref = null;
           let refData = typeToRef[state.type];
           if (dataIndex == -1) {
             // parent
             ref = this.$refs[refData.parent];
             if (refData.type === "dialog") {
               ref = ref.$el;
             }
           } else {
             // item
             if (refData.type === "dialog") {
               // starting from the first
               ref = this.$refs[refData.list].children[dataIndex];
             } else {
               // starting from the second
               ref = this.$refs[refData.list].children[dataIndex + 1];
             }
           }
           ref.scrollIntoView({behavior: "smooth", block: "end", inline: "end"});
         });
       }

       return selected;
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
   padding-right: 10px;

   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
   width: calc(30vw - 400px);
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
   flex: 1;
   display: flex;
 }

 .status-left-panel {
   display: flex;
   flex-direction: column;

   /* 30% */
   flex: 3;

   overflow-y: scroll;
 }

 .status-right-panel {
   /* 70% */
   flex: 7;

   display: flex;
   flex-direction: column;
 }

 .files-dialog {
   flex: 2;
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
   height: 100%;
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

 .untrack-area {
   /* overflow-y: scroll; */
 }
</style>
