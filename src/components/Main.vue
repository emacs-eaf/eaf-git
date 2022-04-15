<template>
  <div class="box">
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
      class="page"
      :style="{ 'padding-top': navbarHeight }">
      <Dashboard
        v-if="navCurrentItem == 'Dashboard'"
        :diffs="diffs"
        :diffsType="diffsType"
        :selectItemType="selectItemType"
        :selectItemIndex="selectItemIndex"
        :stageStatusInfo="stageStatusInfo"
        :unstageStatusInfo="unstageStatusInfo"
        :untrackStatusInfo="untrackStatusInfo"
        :pyobject="pyobject"
        :unpushInfo="unpushInfo"
        :stashInfo="stashInfo"
        :idColor="idColor"
        :indexColor="authorColor"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"/>
      <Log
        v-if="navCurrentItem == 'Log'"
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
        :selectBranchIndex="selectBranchIndex"
        :selectColor="selectColor"
        :backgroundColor="backgroundColor"
        :currentColor="dateColor"
        :currentBranch="currentBranch"
        :branchInfo="branchInfo"
      />
      <Stash
        v-if="navCurrentItem == 'Stash'"
        :pyobject="pyobject"
        :currentStashIndex="currentStashIndex"
        :stashInfo="stashInfo"
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
 
 import { updateListItemBackground, updateListItemMatchColor, updateListIndex } from "./utils.js"

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
         if (this.branchInfo.length > 0) {
           updateListItemBackground(this.branchInfo, oldVal, val, this.backgroundColor, this.selectColor);
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
     branchInfo: {
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
         }
       },
       deep: true
     },
     unstageStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         if (this.stageStatusInfo.length == 0 && this.unstageStatusInfo.length == 0 && this.untrackStatusInfo.length == 0) {
           this.diffs = "";
         }
       },
       deep: true
     },
     untrackStatusInfo: {
       // eslint-disable-next-line no-unused-vars
       handler: function (val, oldVal) {
         if (this.stageStatusInfo.length == 0 && this.unstageStatusInfo.length == 0 && this.untrackStatusInfo.length == 0) {
           this.diffs = "";
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
       diffsType: "",
       selectItemType: "",
       selectItemIndex: -1,
       stageStatusInfo: [],
       unstageStatusInfo: [],
       untrackStatusInfo: [],
       unpushInfo: "",
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
       stashInfo: [],
       submoduleInfo: [],
       currentSubmoduleIndex: 0,
       currentBranch: "",
       branchInfo: [],
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
     } else if (this.unstageStatusInfo) {
       this.selectItemType = "unstage";
       this.selectItemIndex = -1;
     } else if (this.stageStatusInfo) {
       this.selectItemType = "stage";
       this.selectItemIndex = -1;
     }

     let that = this;

     this.$root.$on("statusSelectNext", function () {
       that.statusSelectNext();
     });

     this.$root.$on("statusSelectPrev", function () {
       that.statusSelectPrev();
     });

     this.currentLogIndex = 0;
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

     this.selectBranchIndex = this.branchInfo.indexOf(this.currentBranch);
     this.$root.$on("branchSelectNext", function () {
       that.branchSelectNext();
     });

     this.$root.$on("branchSelectPrev", function () {
       that.branchSelectPrev();
     });

     this.$root.$on("branchSelectLast", function () {
       that.branchSelectLast();
     });

     this.$root.$on("branchSelectFirst", function () {
       that.branchSelectFirst();
     });

     this.currentSubmoduleIndex = 0;
     this.$root.$on("submoduleSelectNext", function () {
       that.submoduleSelectNext();
     });

     this.$root.$on("submoduleSelectPrev", function () {
       that.submoduleSelectPrev();
     });

     this.$root.$on("submoduleSelectLast", function () {
       that.submoduleSelectLast();
     });

     this.$root.$on("submoduleSelectFirst", function () {
       that.submoduleSelectFirst();
     });

     this.currentStashIndex = 0;
     this.$root.$on("stashSelectNext", function () {
       that.stashSelectNext();
     });

     this.$root.$on("stashSelectPrev", function () {
       that.stashSelectPrev();
     });

     this.$root.$on("stashSelectLast", function () {
       that.stashSelectLast();
     });

     this.$root.$on("stashSelectFirst", function () {
       that.stashSelectFirst();
     });

     this.$root.$on("pageSelectPrev", function () {
       that.pageSelectPrev();
     });

     this.$root.$on("pageSelectNext", function () {
       that.pageSelectNext();
     });

     this.$root.$on("logMarkFile", function () {
       that.logMarkFile();
     });

     this.$root.$on("logUnmarkFile", function () {
       that.logUnmarkFile();
     });

     this.$root.$on("logUnmarkAll", function () {
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
           that.$root.$emit(that.keybindingInfo["Global"][event_key]["command"])
         }
       }

       for (const [module_name, key_dict] of Object.entries(that.keybindingInfo)) {
         if (that.navCurrentItem === module_name) {
           if (event_key in key_dict) {
             that.$root.$emit(key_dict[event_key]["command"]);
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
   methods: {
     init(backgroundColor, foregroundColor, selectColor, panelColor, textColor, navItemActiveColor, infoColor,
          dateColor, idColor, authorColor, matchColor,
          repoPath, repoLastCommitId, repoLastCommitMessage, keybindingInfo) {
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

     updateStashInfo(stashInfo) {
       this.stashInfo = stashInfo;
     },

     updateSubmoduleInfo(submoduleInfo) {
       this.submoduleInfo = submoduleInfo;
       
       if (this.submoduleInfo.length > 0) {
         this.submoduleInfo[0].backgroundColor = this.selectColor;
       }
     },

     updateBranchInfo(currentBranch, branchInfo) {
       this.currentBranch = currentBranch
       this.branchInfo = branchInfo;
       
       this.selectBranchIndex = 0;
       if (this.branchInfo.length > 0) {
         this.branchInfo[0].backgroundColor = this.selectColor;
       }

       this.repoHeadName = currentBranch
     },

     updateChangeDiff(diffsType, diffString) {
       this.diffs = diffString;
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
         } else {
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
       if (this.selectBranchIndex < this.branchInfo.length - 1) {
         this.selectBranchIndex += 1;
       }
     },

     branchSelectPrev() {
       if (this.selectBranchIndex > 0) {
         this.selectBranchIndex -= 1;
       }
     },

     branchSelectLast() {
       this.selectBranchIndex = this.branchInfo.length - 1;
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
       if (this.stashInfo.length > 0 && this.currentStashIndex < this.stashInfo.length - 1) {
         this.currentStashIndex++;
       }
     },

     stashSelectLast() {
       if (this.stashInfo.length > 0 && this.currentStashIndex < this.stashInfo.length - 1) {
         this.currentStashIndex = this.stashInfo.length - 1;
       }
     },

     stashSelectPrev() {
       if (this.stashInfo.length > 0 && this.currentStashIndex > 0) {
         this.currentStashIndex--;
       }
     },

     stashSelectFirst() {
       if (this.stashInfo.length > 0 && this.currentStashIndex > 0) {
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
   }
 }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .box {
   display: flex;
   flex-direction: column;
   width: 100%;
   height: 100%;
 }

 .nav-bar {
   display: flex;
   flex-direction: row;
   width: 100%;
   align-items: center;
   font-size: 18px;

   position: fixed;
   z-index: 999;
   top: 0;
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
   position: relative;
   z-index: 99;
   width: 100%;
 }

 .help-area {
   display: flex;
   flex-direction: row;
   align-items: center;

   overflow-x: scroll;

   padding-top: 10px;
   padding-bottom: 20px;
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
</style>
