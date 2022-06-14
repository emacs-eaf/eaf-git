
<template>
  <div class="box" :style="cssVars">
    <div
      class="nav-bar"
      :style="{ 'height': navbarHeight, 'background': backgroundColor }">
      <div
        class="nav-item"
        v-for="(item, index) in navItems"
        :key="item"
        :style="{ 'color': navItemForegroundColor(item), 'background': navItemBackgroundColor(item) }">
        {{ item }} [{{ index + 1 }}]
      </div>
      <div
        class="repo-info"
        :style="{ 'color': infoColor }">
        {{ repoPath }} ({{ repoHeadName }}) {{ repoLastCommitId.slice(0, 7) }} {{ repoLastCommitMessage }}
      </div>
    </div>
    <div
      class="page">
      <Dashboard
        v-if="navCurrentItem == 'Dashboard'"
        :layoutClass="layoutClass"
        :diffs="diffs"
        :diffsType="diffsType"
        :patchSet="patchSet"

        :selectItemType="selectItemType"
        :selectItemIndex="selectItemIndex"
        :selectPatchIndex="selectPatchIndex"
        :selectHunkIndex="selectHunkIndex"
        :stageStatusInfo="stageStatusInfo"
        :unstageStatusInfo="unstageStatusInfo"
        :untrackStatusInfo="untrackStatusInfo"

        :statusState = "statusState"

        :pyobject="pyobject"
        :unpushStatusInfo="unpushStatusInfo"
        :stashStatusInfo="stashStatusInfo"
        :idColor="idColor"
        :indexColor="authorColor"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"/>
      <Log
        v-if="navCurrentItem == 'Log'"
        :layoutClass="layoutClass"
        :pyobject="pyobject"
        :currentLogIndex="currentLogIndex"
        :logBranch="logBranch"
        :logInfo="logInfo"
        :compareLogBranch="compareLogBranch"
        :compareLogInfo="compareLogInfo"
        :idColor="idColor"
        :dateColor="dateColor"
        :markColor="navItemActiveColor"
        :matchColor="matchColor"
        :authorColor="authorColor"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"
        :searchLogKeyword="searchLogKeyword"
        :searchLogMatchNumber="searchLogMatchNumber"
        :searchLogIndex="searchLogIndex"
        v-on:updateLogIndex="updateLogIndex"/>
      <Submodule
        v-if="navCurrentItem == 'Submodule'"
        :pyobject="pyobject"
        :submoduleInfo="submoduleInfo"
        :currentSubmoduleIndex="currentSubmoduleIndex"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"
        :searchSubmoduleKeyword="searchSubmoduleKeyword"
        :searchSubmoduleMatchNumber="searchSubmoduleMatchNumber"
        :searchSubmoduleIndex="searchSubmoduleIndex"
        v-on:updateSubmoduleIndex="updateSubmoduleIndex"/>
      <Branch
        v-if="navCurrentItem == 'Branch'"
        :layoutClass="layoutClass"
        :selectBranchIndex="selectBranchIndex"
        :selectColor="selectColor"
        :backgroundColor="backgroundColor"
        :currentColor="dateColor"
        :currentBranch="currentBranch"
        :localBranchInfo="localBranchInfo"
        :remoteBranchInfo="remoteBranchInfo"
      />
      <Stash
        v-if="navCurrentItem == 'Stash'"
        :pyobject="pyobject"
        :currentStashIndex="currentStashIndex"
        :stashStatusInfo="stashStatusInfo"
        :idColor="idColor"
        :dateColor="dateColor"
        :indexColor="authorColor"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"/>
    </div>
    <div class="help-area">
      <div
        class="help-item"
        :style="{ 'color': idColor }"
        v-for="(info, index) in keyDescriptionList"
        :key="index">
        <div class="help-key">
          {{ info["description"] }}
        </div>
        <div class="help-description">
          [{{ info["key"] }}]
        </div>
      </div>
    </div>
  </div>
</template>

<script>
 import { QWebChannel } from "qwebchannel";

 import Dashboard from "./Dashboard.vue"
 import Log from "./Log.vue"
 import Submodule from "./Submodule.vue"
 import Branch from "./Branch.vue"
 import Stash from "./Stash.vue"

 import { Layout, updateListItemBackground, updateListItemMatchColor, updateListIndex } from "./utils.js"

 export default {
   name: 'Main',
   components: {
     Dashboard,
     Log,
     Submodule,
     Branch,
     Stash
   },
   props: {
   },
   watch: {
     selectBranchIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.localBranchInfo.length > 0) {
           updateListItemBackground(this.localBranchInfo, oldVal, val, this.backgroundColor, this.selectColor);
         }
       }
     },
     currentLogIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           updateListItemBackground(this.logInfo, oldVal, val, this.backgroundColor, this.selectColor);
         }
       }
     },
     searchLogMatchIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.logInfo.length > 0) {
           updateListItemMatchColor(this.logInfo, oldVal, val, this.matchColor);
         }
       }
     },
     searchSubmoduleMatchIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.submoduleInfo.length > 0) {
           updateListItemMatchColor(this.submoduleInfo, oldVal, val, this.matchColor);
         }
       }
     },
     currentSubmoduleIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.submoduleInfo.length > 0) {
           updateListItemBackground(this.submoduleInfo, oldVal, val, this.backgroundColor, this.selectColor);
         }
       }
     },
     localBranchInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         window.pyobject.vue_update_branch_status(val);
       },
       deep: true
     },
     stageStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         if (this.stageStatusInfo.length == 0 && this.unstageStatusInfo.length == 0 && this.untrackStatusInfo.length == 0) {
           this.diffs = "";
           this.patchSet = [];
         }
       },
       deep: true
     },
     unstageStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         if (this.stageStatusInfo.length == 0 && this.unstageStatusInfo.length == 0 && this.untrackStatusInfo.length == 0) {
           this.diffs = "";
           this.patchSet = [];
         }
       },
       deep: true
     },
     untrackStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         if (this.stageStatusInfo.length == 0 && this.unstageStatusInfo.length == 0 && this.untrackStatusInfo.length == 0) {
           this.diffs = "";
           this.patchSet = [];
         }
       },
       deep: true
     },
     navCurrentItem: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         window.pyobject.vue_update_nav_current_item(val);
       },
       deep: true
     }
   },
   data() {
     return {
       layout: Layout.Horizontal,
       navbarHeight: "40px",
       navItems: ["Dashboard", "Log", "Branch", "Stash", "Submodule"],
       navCurrentItem: "Dashboard",
       backgroundColor: "",
       foregroundColor: "",
       selectColor: "",
       panelColor: "",
       textColor: "",
       navItemActiveColor: "",
       infoColor: "",
       dateColor: "",
       idColor: "",
       authorColor: "",
       matchColor: "",
       repoHeadName: "",
       repoLastCommitId: "",
       repoLastCommitMessage: "",
       repoPath: "",
       currentLogIndex: 0,
       currentStashIndex: 0,
       diffs: "",
       patchSet: [],
       diffsType: "",

       // untracked, unstaged, staged, stash, unpushed
       statusState: {},

       selectPatchType: "",
       selectPatchIndex: -1,
       selectHunkType: "",
       selectHunkIndex: -1,
       selectItemType: "",
       selectItemIndex: -1,
       stageStatusInfo: [],
       unstageStatusInfo: [],
       untrackStatusInfo: [],
       unpushStatusInfo: "",

       logBranch: "",
       selectBranchIndex: 0,
       logInfo: [],
       searchLogMatchIndexes: [],
       searchLogMatchNumber: 0,
       searchLogStartIndex: -1,
       searchLogIndex: 0,
       searchLogMatchIndex: null,
       searchLogKeyword: "",
       searchSubmoduleMatchIndexes: [],
       searchSubmoduleMatchNumber: 0,
       searchSubmoduleStartIndex: -1,
       searchSubmoduleIndex: 0,
       searchSubmoduleMatchIndex: null,
       searchSubmoduleKeyword: "",
       compareLogBranch: "",
       compareLogInfo: [],
       stashStatusInfo: [],
       submoduleInfo: [],
       currentSubmoduleIndex: 0,
       currentBranch: "",
       localBranchInfo: [],
       remoteBranchInfo: [],
       keybindingInfo: [],
       keyDescriptionList: [],
       pyobject: null
     }
   },
   mounted() {
     window.init = this.init;
     window.changePage = this.changePage;
     window.updateLogInfo = this.updateLogInfo;
     window.updateCompareLogInfo = this.updateCompareLogInfo;
     window.updateStashInfo = this.updateStashInfo;
     window.updateSubmoduleInfo = this.updateSubmoduleInfo;
     window.updateBranchInfo = this.updateBranchInfo;
     window.updateLocalBranchInfo = this.updateLocalBranchInfo;
     window.updateStatusInfo = this.updateStatusInfo;
     window.updateUnpushInfo = this.updateUnpushInfo;
     window.updateSelectInfo = this.updateSelectInfo;
     window.updateChangeDiff = this.updateChangeDiff;
     window.searchLogsStart = this.searchLogsStart;
     window.searchLogsFinish = this.searchLogsFinish;
     window.searchLogsCancel = this.searchLogsCancel;
     window.searchLogsJumpNext = this.searchLogsJumpNext;
     window.searchLogsJumpPrev = this.searchLogsJumpPrev;
     window.searchSubmodulesStart = this.searchSubmodulesStart;
     window.searchSubmodulesFinish = this.searchSubmodulesFinish;
     window.searchSubmodulesCancel = this.searchSubmodulesCancel;
     window.searchSubmodulesJumpNext = this.searchSubmodulesJumpNext;
     window.searchSubmodulesJumpPrev = this.searchSubmodulesJumpPrev;

     if (this.untrackStatusInfo) {
       this.selectItemType = "untrack";
       this.selectItemIndex = -1;
       this.selectPatchIndex = -1;
       this.selectHunkIndex = -1;
     } else if (this.unstageStatusInfo) {
       this.selectItemType = "unstage";
       this.selectItemIndex = -1;
       this.selectPatchIndex = -1;
       this.selectHunkIndex = -1;
     } else if (this.stageStatusInfo) {
       this.selectItemType = "stage";
       this.selectItemIndex = -1;
       this.selectPatchIndex = -1;
       this.selectHunkIndex = -1;
     }

     let that = this;

     this.$root.$on("toggle_layout", function () {
       that.toggleLayout();
     });

     this.$root.$on("status_select_next", function () {
       that.statusSelectNext();
     });

     this.$root.$on("status_select_prev", function () {
       that.statusSelectPrev();
     });

     this.$root.$on("hunks_select_next", function () {
       that.hunksSelectNext();
     });

     this.$root.$on("hunks_select_prev", function () {
       that.hunksSelectPrev();
     });

     this.currentLogIndex = 0;
     this.$root.$on("log_select_next", function () {
       that.logSelectNext();
     });

     this.$root.$on("log_select_prev", function () {
       that.logSelectPrev();
     });

     this.$root.$on("log_select_last", function () {
       that.logSelectLast();
     });

     this.$root.$on("log_select_first", function () {
       that.logSelectFirst();
     });

     this.selectBranchIndex = this.localBranchInfo.indexOf(this.currentBranch);
     this.$root.$on("branch_select_next", function () {
       that.branchSelectNext();
     });

     this.$root.$on("branch_select_prev", function () {
       that.branchSelectPrev();
     });

     this.$root.$on("branch_select_last", function () {
       that.branchSelectLast();
     });

     this.$root.$on("branch_select_first", function () {
       that.branchSelectFirst();
     });

     this.currentSubmoduleIndex = 0;
     this.$root.$on("submodule_select_next", function () {
       that.submoduleSelectNext();
     });

     this.$root.$on("submodule_select_prev", function () {
       that.submoduleSelectPrev();
     });

     this.$root.$on("submodule_select_last", function () {
       that.submoduleSelectLast();
     });

     this.$root.$on("submodule_select_first", function () {
       that.submoduleSelectFirst();
     });

     this.currentStashIndex = 0;
     this.$root.$on("stash_select_next", function () {
       that.stashSelectNext();
     });

     this.$root.$on("stash_select_prev", function () {
       that.stashSelectPrev();
     });

     this.$root.$on("stash_select_last", function () {
       that.stashSelectLast();
     });

     this.$root.$on("stash_select_first", function () {
       that.stashSelectFirst();
     });

     this.$root.$on("page_select_prev", function () {
       that.pageSelectPrev();
     });

     this.$root.$on("page_select_next", function () {
       that.pageSelectNext();
     });

     this.$root.$on("log_mark_file", function () {
       that.logMarkFile();
     });

     this.$root.$on("log_unmark_file", function () {
       that.logUnmarkFile();
     });

     this.$root.$on("log_unmark_all", function () {
       that.logUnmarkAll();
     });

     window.addEventListener('keydown', function(event) {
       var event_key = event.key;

       if (event_key === "1") {
         that.changePage("Dashboard");
       } else if (event_key === "2") {
         that.changePage("Log");
       } else if (event_key === "3") {
         that.changePage("Branch");
       } else if (event_key === "4") {
         that.changePage("Stash");
       } else if (event_key === "5") {
         that.changePage("Submodule");
       } else if (event_key === "6") {
         that.changePage("Patch");
       } else {
         if (event_key in that.keybindingInfo["Global"]) {
           that.execute_command(that.keybindingInfo["Global"][event_key]["command"]);
         }
       }

       for (const [module_name, key_dict] of Object.entries(that.keybindingInfo)) {
         if (that.navCurrentItem === module_name) {
           if (event_key in key_dict) {
             that.execute_command(key_dict[event_key]["command"]);
           }
         }
       }
     });
   },
   created() {
     // eslint-disable-next-line no-undef
     new QWebChannel(qt.webChannelTransport, channel => {
       window.pyobject = channel.objects.pyobject;
       this.pyobject = window.pyobject;
     });
   },
   computed: {
     cssVars() {
       return {
         '--select-color': this.selectColor
       };
     },
     layoutClass() {
       return this.layout === Layout.Vertical ? "layout-vertical" : "layout-horizontal";
     },
   },
   methods: {
     init(layout,
          backgroundColor, foregroundColor, selectColor, panelColor, textColor, navItemActiveColor, infoColor,
          dateColor, idColor, authorColor, matchColor,
          repoPath, repoLastCommitId, repoLastCommitMessage, keybindingInfo) {
       this.layout = layout;
       this.backgroundColor = backgroundColor;
       this.foregroundColor = foregroundColor;
       this.selectColor = selectColor;
       this.panelColor = panelColor;
       this.textColor = textColor;
       this.navItemActiveColor = navItemActiveColor;
       this.infoColor = infoColor;
       this.dateColor = dateColor;
       this.idColor = idColor;
       this.authorColor = authorColor;
       this.matchColor = matchColor;
       this.repoPath = repoPath;
       this.repoLastCommitId = repoLastCommitId;
       this.repoLastCommitMessage = repoLastCommitMessage["lastCommit"];
       this.keybindingInfo = keybindingInfo;

       this.updateKeyDescriptionList();
     },

     navItemForegroundColor(item) {
       if (item == this.navCurrentItem) {
         return this.navItemActiveColor;
       } else {
         return this.textColor;
       }
     },

     navItemBackgroundColor() {
       return "";
     },

     toggleLayout() {
       if (this.layout === Layout.Horizontal) {
         this.layout = Layout.Vertical;
       } else {
         this.layout = Layout.Horizontal;
       }
     },

     changePage(pageName) {
       this.navCurrentItem = pageName;

       this.updateKeyDescriptionList();
     },

     pageSelectPrev() {
       var index = this.navItems.indexOf(this.navCurrentItem);

       if (index > 0) {
         this.changePage(this.navItems[index - 1]);
       }
     },

     pageSelectNext() {
       var index = this.navItems.indexOf(this.navCurrentItem);

       if (index < this.navItems.length - 1) {
         this.changePage(this.navItems[index + 1]);
       }
     },

     /**
      * Add state for the data list
      */
     addStateForStatusInfo(states, type, dataList) {
       let stateStartIndex = -1;

       // only when there are data in the list
       if (dataList.length > 0) {
         stateStartIndex = states.length;

         // list container
         states.push({
           type: type,
           dataIndex: -1,
           selected: false
         });

         // list item
         for (let index = 0; index < dataList.length; index++) {
           states.push({
             type: type,
             dataIndex: index,
             selected: false
           });
         }
       }

       return stateStartIndex;
     },
     /**
      * Create status state for selection
      */
     createStatusState() {
       // initialize the status info
       let statusState = {};

       // data references
       let dataRef = {
         "status": {
           stateStartIndex: 0
         },
         "untrack": {},
         "unstage": {},
         "stage": {},
         "stash": {},
         "unpush": {}
       };
       statusState.dataRef = dataRef;

       // selection state
       let states = [];
       statusState.states = states;

       states.push({
         type: "status",
         dataIndex: -1,
         selected: false
       });

       // untracked
       dataRef.untrack.stateStartIndex = this.addStateForStatusInfo(states, "untrack", this.untrackStatusInfo);
       // unstaged
       dataRef.unstage.stateStartIndex = this.addStateForStatusInfo(states, "unstage", this.unstageStatusInfo);
       // staged
       dataRef.stage.stateStartIndex = this.addStateForStatusInfo(states, "stage", this.stageStatusInfo);
       // stashes
       dataRef.stash.stateStartIndex = this.addStateForStatusInfo(states, "stash", this.stashStatusInfo);
       // unpushed
       dataRef.unpush.stateStartIndex = this.addStateForStatusInfo(states, "unpush", this.unpushStatusInfo);

       if (!this.selectItemType) {
         this.selectItemType = "status";
       }

       let selectedData = dataRef[this.selectItemType];
       let selectIndex = selectedData.stateStartIndex + this.selectItemIndex + 1;
       states[selectIndex].selected = true;
       statusState.selectIndex = selectIndex;

       this.statusState = statusState;
     },

     updateSelectInfo(stageStatusInfo, unstageStatusInfo, untrackStatusInfo, selectItemType, selectItemIndex) {
       this.stageStatusInfo = stageStatusInfo;
       this.unstageStatusInfo = unstageStatusInfo;
       this.untrackStatusInfo = untrackStatusInfo;
       this.selectItemIndex = selectItemIndex;
       this.selectItemType = selectItemType;

       this.createStatusState();
     },

     updateStatusInfo(stageStatusInfo, unstageStatusInfo, untrackStatusInfo) {
       this.stageStatusInfo = stageStatusInfo;
       this.unstageStatusInfo = unstageStatusInfo;
       this.untrackStatusInfo = untrackStatusInfo;

       this.createStatusState();
     },

     updateUnpushInfo(unpushStatusInfo) {
       this.unpushStatusInfo = unpushStatusInfo;
     },

     updateKeyDescriptionList() {
       for (const [module_name, key_dict] of Object.entries(this.keybindingInfo)) {
         if (this.navCurrentItem === module_name) {
           var description_list = [] ;
           for (const [key, value] of Object.entries(key_dict)) {
             description_list.push({
               "key": key,
               "description": value["description"]
             });
           }

           for (const [key, value] of Object.entries(this.keybindingInfo["Global"])) {
             description_list.push({
               "key": key,
               "description": value["description"]
             });
           }

           this.keyDescriptionList = description_list;
           return;
         }
       }

       this.keyDescriptionList = [];
     },

     updateLogInfo(logBranch, logInfo) {
       this.logBranch = logBranch;
       this.logInfo = logInfo;

       if (this.logInfo.length > 0) {
         this.logInfo[0].backgroundColor = this.selectColor;
       }
     },

     updateCompareLogInfo(compareLogBranch, compareLogInfo) {
       this.compareLogBranch = compareLogBranch;
       this.compareLogInfo = compareLogInfo;
     },

     updateStashInfo(stashStatusInfo) {
       this.stashStatusInfo = stashStatusInfo;
     },

     updateSubmoduleInfo(submoduleInfo) {
       this.submoduleInfo = submoduleInfo;

       if (this.submoduleInfo.length > 0) {
         this.submoduleInfo[0].backgroundColor = this.selectColor;
       }
     },

     updateBranchInfo(currentBranch, localBranchInfo, remoteBranchInfo) {
       this.currentBranch = currentBranch
       this.localBranchInfo = localBranchInfo;
       this.remoteBranchInfo = remoteBranchInfo;

       this.selectBranchIndex = 0;
       if (this.localBranchInfo.length > 0) {
         this.localBranchInfo[0].backgroundColor = this.selectColor;
       }

       this.repoHeadName = currentBranch
     },

     updateLocalBranchInfo(currentBranch, localBranchInfo) {
       this.currentBranch = currentBranch
       this.localBranchInfo = localBranchInfo;

       this.selectBranchIndex = 0;
       if (this.localBranchInfo.length > 0) {
         this.localBranchInfo[0].backgroundColor = this.selectColor;
       }

       this.repoHeadName = currentBranch
     },

     updateChangeDiff(diffsType, diffInfo) {
       this.diffs = diffInfo["diff"];
       this.patchSet = diffInfo["patch_set"];
       this.diffsType = diffsType;
     },

     updateDiff() {
       if (this.selectItemIndex === -1) {
         this.pyobject.update_diff(this.selectItemType, "");
       } else {
         if (this.selectItemType === "untrack") {
           this.pyobject.update_diff(this.selectItemType, this.untrackStatusInfo[this.selectItemIndex].file);
         } else if (this.selectItemType === "unstage") {
           this.pyobject.update_diff(this.selectItemType, this.unstageStatusInfo[this.selectItemIndex].file);
         } else if (this.selectItemType === "stage") {
           this.pyobject.update_diff(this.selectItemType, this.stageStatusInfo[this.selectItemIndex].file);
         }
       }
     },

     searchLogsStart(keyword, matchIndexes) {
       if (this.searchLogStartIndex == -1) {
         this.searchLogStartIndex = this.currentLogIndex;
       }

       this.searchLogKeyword = keyword;
       this.searchLogIndex = 0;

       this.searchLogMatchIndexes = matchIndexes;
       this.searchLogMatchNumber = this.searchLogMatchIndexes.length;

       this.currentLogIndex = this.searchLogMatchIndexes[0];
       this.searchLogMatchIndex = this.currentLogIndex;
     },

     searchLogsJumpNext() {
       if (this.searchLogIndex >= this.searchLogMatchNumber - 1) {
         this.searchLogIndex = 0;
       } else {
         this.searchLogIndex++;
       }

       this.currentLogIndex = this.searchLogMatchIndexes[this.searchLogIndex];
       this.searchLogMatchIndex = this.currentLogIndex;
     },

     searchLogsJumpPrev() {
       if (this.searchLogIndex <= 0) {
         this.searchLogIndex = this.searchLogMatchNumber - 1;
       } else {
         this.searchLogIndex--;
       }

       this.currentLogIndex = this.searchLogMatchIndexes[this.searchLogIndex];
       this.searchLogMatchIndex = this.currentLogIndex;
     },

     searchLogsFinish() {
       this.searchLogStartIndex = -1;
       this.searchLogKeyword = "";
       this.searchLogIndex = 0;
       this.searchLogMatchIndexes = [];
       this.searchLogMatchNumber = 0;
       this.searchLogMatchIndex = null;
     },

     searchLogsCancel() {
       this.currentLogIndex = this.searchLogStartIndex;

       this.searchLogStartIndex = -1;
       this.searchLogKeyword = "";
       this.searchLogIndex = 0;
       this.searchLogMatchIndexes = [];
       this.searchLogMatchNumber = 0;
       this.searchLogMatchIndex = null;
     },

     searchSubmodulesStart(keyword, matchIndexes) {
       if (this.searchSubmoduleStartIndex == -1) {
         this.searchSubmoduleStartIndex = this.currentSubmoduleIndex;
       }

       this.searchSubmoduleKeyword = keyword;
       this.searchSubmoduleIndex = 0;

       this.searchSubmoduleMatchIndexes = matchIndexes;
       this.searchSubmoduleMatchNumber = this.searchSubmoduleMatchIndexes.length;

       this.currentSubmoduleIndex = this.searchSubmoduleMatchIndexes[0];
       this.searchSubmoduleMatchIndex = this.currentSubmoduleIndex;
     },

     searchSubmodulesJumpNext() {
       if (this.searchSubmoduleIndex >= this.searchSubmoduleMatchNumber - 1) {
         this.searchSubmoduleIndex = 0;
       } else {
         this.searchSubmoduleIndex++;
       }

       this.currentSubmoduleIndex = this.searchSubmoduleMatchIndexes[this.searchSubmoduleIndex];
       this.searchSubmoduleMatchIndex = this.currentSubmoduleIndex;
     },

     searchSubmodulesJumpPrev() {
       if (this.searchSubmoduleIndex <= 0) {
         this.searchSubmoduleIndex = this.searchSubmoduleMatchNumber - 1;
       } else {
         this.searchSubmoduleIndex--;
       }

       this.currentSubmoduleIndex = this.searchSubmoduleMatchIndexes[this.searchSubmoduleIndex];
       this.searchSubmoduleMatchIndex = this.currentSubmoduleIndex;
     },

     searchSubmodulesFinish() {
       this.searchSubmoduleStartIndex = -1;
       this.searchSubmoduleKeyword = "";
       this.searchSubmoduleIndex = 0;
       this.searchSubmoduleMatchIndexes = [];
       this.searchSubmoduleMatchNumber = 0;
       this.searchSubmoduleMatchIndex = null;
     },

     searchSubmodulesCancel() {
       this.currentSubmoduleIndex = this.searchSubmoduleStartIndex;

       this.searchSubmoduleStartIndex = -1;
       this.searchSubmoduleKeyword = "";
       this.searchSubmoduleIndex = 0;
       this.searchSubmoduleMatchIndexes = [];
       this.searchSubmoduleMatchNumber = 0;
       this.searchSubmoduleMatchIndex = null;
     },

     statusSelectNext() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       let selectIndex = this.statusState.selectIndex;
       let states = this.statusState.states;
       let lastState = states[selectIndex];
       // unselect last state
       lastState.selected = false;

       if (selectIndex == states.length - 1) {
         // selectIndex = 0;
       } else {
         selectIndex++;
       }

       // new state
       let state = states[selectIndex];
       state.selected = true;

       // new index and new type / item
       this.statusState.selectIndex = selectIndex;
       this.selectItemType = state.type;
       this.selectItemIndex = state.dataIndex;

       if (oldSelectItemType != this.selectItemType ||
           oldSelectItemIndex != this.selectItemIndex) {
         this.selectPatchIndex = -1;
         this.selectHunkIndex = -1;
         this.updateDiff();
       }
     },

     statusSelectPrev() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       let selectIndex = this.statusState.selectIndex;
       let states = this.statusState.states;
       let lastState = states[selectIndex];
       // unselect last state
       lastState.selected = false;

       if (selectIndex == 0) {
         // selectIndex = 0;
       } else {
         selectIndex--;
       }

       // new state
       let state = states[selectIndex];
       state.selected = true;

       // new index and new type / item
       this.statusState.selectIndex = selectIndex;
       this.selectItemType = state.type;
       this.selectItemIndex = state.dataIndex;

       if (oldSelectItemType != this.selectItemType ||
           oldSelectItemIndex != this.selectItemIndex) {
         this.selectPatchIndex = -1;
         this.selectHunkIndex = -1;
         this.updateDiff();
       }
     },

     hunksSelectNext() {
       const oldSelectPatchIndex = this.selectPatchIndex;
       const oldSelectHunkIndex = this.selectHunkIndex;
       if (this.patchSet.length > 0) {
         if (this.selectPatchIndex === -1 && this.selectHunkIndex === -1) {
           this.selectPatchIndex = 0;
           this.selectHunkIndex = 0;
         } else {
           for (let pIndex = this.selectPatchIndex; pIndex < this.patchSet.length; pIndex++) {
             for (let hIndex = this.selectHunkIndex; hIndex < this.patchSet[pIndex]['diff_hunks'].length; hIndex++) {
               if (this.patchSet[pIndex] && this.patchSet[pIndex]['diff_hunks'][hIndex]) {
                 if (pIndex !== oldSelectPatchIndex || hIndex !== oldSelectHunkIndex) {
                   this.selectPatchIndex = pIndex;
                   this.selectHunkIndex = hIndex;
                   return;
                 }
               }
             }
           }
         }
       }
     },

     hunksSelectPrev() {
       const oldSelectPatchIndex = this.selectPatchIndex;
       const oldSelectHunkIndex = this.selectHunkIndex;
       for (let pIndex = this.selectPatchIndex; pIndex > -1; pIndex--) {
         for (let hIndex = this.selectHunkIndex; hIndex > -1; hIndex--) {
           if (this.patchSet[pIndex] && this.patchSet[pIndex]['diff_hunks'][hIndex]) {
             if (pIndex !== oldSelectPatchIndex || hIndex !== oldSelectHunkIndex) {
               this.selectPatchIndex = pIndex;
               this.selectHunkIndex = hIndex;
               return;
             }
           }
         }
       }
     },

     logSelectNext() {
       if (this.logInfo.length > 0 && this.currentLogIndex < this.logInfo.length - 1) {
         this.currentLogIndex++;
       }
     },

     logSelectLast() {
       if (this.logInfo.length > 0 && this.currentLogIndex < this.logInfo.length - 1) {
         this.currentLogIndex = this.logInfo.length - 1;
       }
     },

     logSelectPrev() {
       if (this.logInfo.length > 0 && this.currentLogIndex > 0) {
         this.currentLogIndex--;
       }
     },

     logSelectFirst() {
       if (this.logInfo.length > 0 && this.currentLogIndex > 0) {
         this.currentLogIndex = 0;
       }
     },

     branchSelectNext() {
       if (this.selectBranchIndex < this.localBranchInfo.length - 1) {
         this.selectBranchIndex += 1;
       }
     },

     branchSelectPrev() {
       if (this.selectBranchIndex > 0) {
         this.selectBranchIndex -= 1;
       }
     },

     branchSelectLast() {
       this.selectBranchIndex = this.localBranchInfo.length - 1;
     },

     branchSelectFirst() {
       this.selectBranchIndex = 0;
     },

     submoduleSelectNext() {
       if (this.submoduleInfo.length > 0 && this.currentSubmoduleIndex < this.submoduleInfo.length - 1) {
         this.currentSubmoduleIndex++;
       }
     },

     submoduleSelectLast() {
       if (this.submoduleInfo.length > 0 && this.currentSubmoduleIndex < this.submoduleInfo.length - 1) {
         this.currentSubmoduleIndex = this.submoduleInfo.length - 1;
       }
     },

     submoduleSelectPrev() {
       if (this.submoduleInfo.length > 0 && this.currentSubmoduleIndex > 0) {
         this.currentSubmoduleIndex--;
       }
     },

     submoduleSelectFirst() {
       if (this.submoduleInfo.length > 0 && this.currentSubmoduleIndex > 0) {
         this.currentSubmoduleIndex = 0;
       }
     },

     updateLogIndex(index) {
       this.currentLogIndex = updateListIndex(this.logInfo, index);
     },

     updateSubmoduleIndex(index) {
       this.currentSubmoduleIndex = updateListIndex(this.submoduleInfo, index);
     },

     stashSelectNext() {
       if (this.stashStatusInfo.length > 0 && this.currentStashIndex < this.stashStatusInfo.length - 1) {
         this.currentStashIndex++;
       }
     },

     stashSelectLast() {
       if (this.stashStatusInfo.length > 0 && this.currentStashIndex < this.stashStatusInfo.length - 1) {
         this.currentStashIndex = this.stashStatusInfo.length - 1;
       }
     },

     stashSelectPrev() {
       if (this.stashStatusInfo.length > 0 && this.currentStashIndex > 0) {
         this.currentStashIndex--;
       }
     },

     stashSelectFirst() {
       if (this.stashStatusInfo.length > 0 && this.currentStashIndex > 0) {
         this.currentStashIndex = 0;
       }
     },

     logMarkFile() {
       this.logInfo[this.currentLogIndex].foregroundColor = this.navItemActiveColor;
       this.logInfo[this.currentLogIndex].marked = "marked";
       this.logSelectNext();
     },

     logUnmarkFile() {
       this.logInfo[this.currentLogIndex].foregroundColor = "";
       this.logInfo[this.currentLogIndex].marked = "";
       this.logSelectNext();
     },

     logUnmarkAll() {
       for (var i=0; i < this.logInfo.length; i++) {
         this.logInfo[i].foregroundColor = "";
         this.logInfo[i].marked = "";
       }
     },

     execute_command(command) {
       if (command.startsWith("js_")) {
         command = command.replace("js_", "")
         this.$root.$emit(command);
       } else if (command.startsWith("py_")) {
         command = command.replace("py_", "")
         this.pyobject[command]();
       }
     }
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .box {
   flex: 1;
   display: flex;
   flex-direction: column;
 }

 .nav-bar {
   display: flex;
   flex-direction: row;
   align-items: center;
   font-size: 18px;
 }

 .nav-item {
   padding-top: 10px;
   padding-bottom: 10px;
   padding-left: 10px;
   padding-right: 10px;
 }

 .repo-info {
   text-align: right;
   padding-left: 50px;
   padding-right: 10px;
   flex: 1;

   overflow: hidden;
   white-space: nowrap;
   text-overflow: ellipsis;
 }

 .page {
   flex: 1;

   display: flex;
   flex-direction: column;
 }

 .help-area {
   display: flex;
   flex-wrap: wrap;
   line-height: 1.5;
   
   flex-direction: row;
   align-items: center;

   padding-bottom: 10px;
 }

 .help-item {
   display: flex;
   flex-direction: row;
   align-item: center;

   padding-left: 10px;
   padding-right: 10px;

   white-space: nowrap;
 }

 .help-description {
   padding-left: 5px;
 }

 /deep/ .selected {
   background-color: var(--select-color);
 }
</style>

