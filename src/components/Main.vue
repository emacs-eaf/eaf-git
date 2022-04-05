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
        {{ repoPath }} ({{ repoHeadName }}) {{ repoLastCommitId }} {{ repoLastCommitMessage }}
      </div>
    </div>
    <div
      class="page"
      :style="{ 'padding-top': navbarHeight }">
      <Dashboard
        v-if="navCurrentItem == 'Dashboard'"
        :diffs="diffs"
        :selectItemType="selectItemType"
        :selectItemIndex="selectItemIndex"
        :stageStatusInfo="stageStatusInfo"
        :unstageStatusInfo="unstageStatusInfo"
        :untrackStatusInfo="untrackStatusInfo"
        :pyobject="pyobject"
        :unpushInfo="unpushInfo"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"/>
      <Log
        v-if="navCurrentItem == 'Log'"
        :pyobject="pyobject"
        :currentCommitIndex="currentCommitIndex"
        :logInfo="logInfo"
        :idColor="idColor"
        :dateColor="dateColor"
        :authorColor="authorColor"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"/>
      <Submodule
        v-if="navCurrentItem == 'Submodule'"
        :submoduleInfo="submoduleInfo"/>
      <Branch
        v-if="navCurrentItem == 'Branch'"
        :selectColor="selectColor"
        :backgroundColor="backgroundColor"
        :currentColor="dateColor"
        :currentBranch="currentBranch"
        :branchInfo="branchInfo"
      />
      <Patch v-if="navCurrentItem == 'Patch'"/>
      <Stash v-if="navCurrentItem == 'Stash'"/>
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
 import Patch from "./Patch.vue"

 export default {
   name: 'Main',
   components: {
     Dashboard,
     Log,
     Submodule,
     Branch,
     Stash,
     Patch
   },
   props: {
   },
   data() {
     return {
       navbarHeight: "40px",
       navItems: ["Dashboard", "Log", "Branch", "Stash", "Submodule", "Patch"],
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
       repoHeadName: "",
       repoLastCommitId: "",
       repoLastCommitMessage: "",
       repoPath: "",
       currentCommitIndex: 0,
       diffs: "",
       selectItemType: "",
       selectItemIndex: -1,
       stageStatusInfo: [],
       unstageStatusInfo: [],
       untrackStatusInfo: [],
       unpushInfo: "",
       logInfo: [],
       submoduleInfo: [],
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
     window.updateSubmoduleInfo = this.updateSubmoduleInfo;
     window.updateBranchInfo = this.updateBranchInfo;
     window.updateStatusInfo = this.updateStatusInfo;
     window.updateUnpushInfo = this.updateUnpushInfo;
     window.updateSelectInfo = this.updateSelectInfo;
     window.updateChangeDiff = this.updateChangeDiff;
     
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
     
     this.currentCommitIndex = 0;
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
       }

       for (const [module_name, key_dict] of Object.entries(that.keybindingInfo)) {
         if (that.navCurrentItem === module_name) {
           if (event_key in key_dict) {
             that.$root.$emit(key_dict[event_key]["command"])
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
          dateColor, idColor, authorColor,
          repoPath, repoHeadName, repoLastCommitId, repoLastCommitMessage, keybindingInfo) {
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
       this.repoPath = repoPath;
       this.repoHeadName = repoHeadName;
       this.repoLastCommitId = repoLastCommitId;
       this.repoLastCommitMessage = repoLastCommitMessage;
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
           
           this.keyDescriptionList = description_list;
           return;
         }
       }
       
       this.keyDescriptionList = [];
     },

     updateLogInfo(logInfo) {
       this.logInfo = logInfo;
     },

     updateSubmoduleInfo(submoduleInfo) {
       this.submoduleInfo = submoduleInfo;
     },

     updateBranchInfo(currentBranch, branchInfo) {
       this.currentBranch = currentBranch
       this.branchInfo = branchInfo;
     },
     
     updateChangeDiff(diffString) {
       this.diffs = diffString;
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
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex++;
       }
     },

     logSelectLast() {
       if (this.logInfo.length > 0 && this.currentCommitIndex < this.logInfo.length - 1) {
         this.currentCommitIndex = this.logInfo.length - 1;
       }
     },

     logSelectPrev() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex--;
       }
     },

     logSelectFirst() {
       if (this.logInfo.length > 0 && this.currentCommitIndex > 0) {
         this.currentCommitIndex = 0;
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
   padding-right: 10px;
   flex: 1;
 }

 .page {
   flex: 1;
   position: relative;
   z-index: 99;
 }
 
 .help-area {
   display: grid;
   grid-auto-flow: column;
   padding-left: 10px;
   padding-right: 10px;
   padding-top: 10px;
   padding-bottom: 20px;
 }
 
 .help-item {
   display: flex;
   flex-direction: row;
   align-item: center;
 }
 
 .help-description {
   padding-left: 5px;
 }
</style>
