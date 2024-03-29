
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

 import { Layout, updateListItemBackground, updateListItemMatchColor, updateListIndex, regsiterJsFunctions } from "./utils.js"

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
       initialStatusState: {},

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
       unpushStatusInfo: [],

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

     this.selectBranchIndex = this.localBranchInfo.indexOf(this.currentBranch);
     this.currentStashIndex = 0;
     this.currentSubmoduleIndex = 0;
     this.currentLogIndex = 0;

     regsiterJsFunctions(this, ["toggle_layout",
                                "toggle_selection_state",
                                "status_select_next",
                                "status_select_prev",
                                "hunks_select_next",
                                "hunks_select_prev",
                                "log_select_next",
                                "log_select_prev",
                                "log_select_last",
                                "log_select_first",
                                "branch_select_next",
                                "branch_select_prev",
                                "branch_select_last",
                                "branch_select_first",
                                "submodule_select_next",
                                "submodule_select_prev",
                                "submodule_select_last",
                                "submodule_select_first",
                                "stash_select_next",
                                "stash_select_prev",
                                "stash_select_last",
                                "stash_select_first",
                                "page_select_prev",
                                "page_select_next",
                                "log_mark_file",
                                "log_unmark_file",
                                "log_unmark_all"]);

     let that = this;
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
     init(layout, initialStatusState,
          backgroundColor, foregroundColor, selectColor, panelColor, textColor, navItemActiveColor, infoColor,
          dateColor, idColor, authorColor, matchColor,
          repoPath, repoLastCommitId, repoLastCommitMessage, keybindingInfo) {
       this.layout = layout;
       this.initialStatusState = initialStatusState;
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
      * Expand / Collapse current selection if applicable
      */
     toggleSelectionState() {
       let selectIndex = this.statusState.selectIndex;
       let state = this.statusState.states[selectIndex];
       if (state.state === "collapsed") {
         state.state = "expanded";
       } else {
         state.state = "collapsed";
       }
     },

     /**
      * Add state for the data list
      */
     addStateForStatusInfo(states, type, dataRef, dataList) {
       dataRef.stateStartIndex = -1;
       dataRef.size = 0;

       // only when there are data in the list
       if (dataList.length > 0) {
         dataRef.stateStartIndex = states.length;

         let initialState = this.initialStatusState[type];

         // list container
         states.push({
           type: type,
           dataIndex: -1,
           selected: false,
           state: initialState ? initialState : "expanded"
         });

         // list item
         for (let index = 0; index < dataList.length; index++) {
           states.push({
             type: type,
             dataIndex: index,
             selected: false
           });
         }

         dataRef.size = dataList.length + 1;
       }
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
           // the start index of the section in states
           stateStartIndex: 0,
           // the total size of the section (data size + 1)
           size: 1
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

       console.log(this.initialStatusState);
       let initialState = this.initialStatusState["status"];
       states.push({
         type: "status",
         dataIndex: -1,
         selected: false,
         state: initialState ? initialState : "expanded"
       });

       // untracked
       this.addStateForStatusInfo(states, "untrack", dataRef.untrack, this.untrackStatusInfo);
       // unstaged
       this.addStateForStatusInfo(states, "unstage", dataRef.unstage, this.unstageStatusInfo);
       // staged
       this.addStateForStatusInfo(states, "stage", dataRef.stage, this.stageStatusInfo);
       // stashes
       this.addStateForStatusInfo(states, "stash", dataRef.stash, this.stashStatusInfo);
       // unpushed
       this.addStateForStatusInfo(states, "unpush", dataRef.unpush, this.unpushStatusInfo);
       dataRef.status.size = 1 + dataRef.untrack.size + dataRef.unstage.size + dataRef.stage.size;

       if (!this.selectItemType) {
         this.selectItemType = "status";
       }

       let selectIndex = 0;
       let selectedData = dataRef[this.selectItemType];
       // during initialization, the select type may not have data
       if (selectedData.stateStartIndex >= 0) {
         selectIndex = selectedData.stateStartIndex + this.selectItemIndex + 1;
       } else {
         this.selectItemType = "status";
       }
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

       this.createStatusState();
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

     updateLogInfo(logBranch, logInfo, append) {
       this.logBranch = logBranch;

       if (append) {
         this.logInfo = this.logInfo.concat(logInfo);
       } else {
         this.logInfo = logInfo;
         if (this.logInfo.length > 0) {
           this.logInfo[0].backgroundColor = this.selectColor;
         }
       }
     },

     updateCompareLogInfo(compareLogBranch, compareLogInfo, append) {
       this.compareLogBranch = compareLogBranch;

       if (append) {
         this.compareLogInfo = this.compareLogInfo.concat(compareLogInfo);
       } else {
         this.compareLogInfo = compareLogInfo;
       }
     },

     updateStashInfo(stashStatusInfo) {
       this.stashStatusInfo = stashStatusInfo;
     },

     updateSubmoduleInfo(submoduleInfo, keepSelection=false) {
       this.submoduleInfo = submoduleInfo;

       if (this.submoduleInfo.length > 0) {
         let selectIndex = 0
         if (keepSelection) selectIndex = this.currentSubmoduleIndex

         this.submoduleInfo[selectIndex].backgroundColor = this.selectColor;
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

     /**
      * Select next visible section or item
      */
     statusSelectNext() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       let selectIndex = this.statusState.selectIndex;
       let states = this.statusState.states;
       let lastState = states[selectIndex];

       if (selectIndex == states.length - 1) {
         // TODO: cycling or not
         // selectIndex = 0;
         return ;
       }

       if (lastState["state"] === 'collapsed') {
         // find next collapsible container
         let currentDataRef = this.statusState.dataRef[lastState.type];
         let nextCollapsibleIndex = currentDataRef.stateStartIndex + currentDataRef.size;
         if (nextCollapsibleIndex < states.length) {
           selectIndex = nextCollapsibleIndex;
         }
       } else {
         selectIndex ++;
       }

       // unselect last state
       lastState.selected = false;

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

     /**
      * Select previous visible section or item
      */
     statusSelectPrev() {
       var oldSelectItemType = this.selectItemType;
       var oldSelectItemIndex = this.selectItemIndex;

       let selectIndex = this.statusState.selectIndex;
       let states = this.statusState.states;
       let lastState = states[selectIndex];

       if (selectIndex == 0) {
         // no change
         // TODO: cycling
         return ;
       } else {
         let newIndex = selectIndex - 1;
         let newState = states[newIndex];
         let parentStartIndex = this.statusState.dataRef[newState.type].stateStartIndex;

         if (states[0].state === "collapsed"
             && (newState.type === "untrack"
              || newState.type === "unstage"
              || newState.type === "stage")) {
           // whole status is collapsed
           selectIndex = 0;
         } else {
           // check parent's state
           if (states[parentStartIndex].state === "expanded") {
             selectIndex = newIndex;
           } else {
             selectIndex = parentStartIndex;
           }
         }
       }

       // unselect last state
       lastState.selected = false;

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
   width: 100%;
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

   padding-left: 10px;
   padding-right: 10px;
 }

 .help-area {
   display: flex;
   flex-wrap: wrap;
   line-height: 1.5;

   flex-direction: row;
   align-items: center;

   padding-top: 10px;
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
