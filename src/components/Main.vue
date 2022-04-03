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
        :pyobject="pyobject"
        :backgroundColor="backgroundColor"
        :selectColor="selectColor"/>
      <Log
        v-if="navCurrentItem == 'Log'"
        :pyobject="pyobject"
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
        :branchInfo="branchInfo"
      />
      <Patch v-if="navCurrentItem == 'Patch'"/>
    </div>
  </div>
</template>

<script>
 import { QWebChannel } from "qwebchannel";

 import Dashboard from "./Dashboard.vue"
 import Log from "./Log.vue"
 import Submodule from "./Submodule.vue"
 import Branch from "./Branch.vue"
 import Patch from "./Patch.vue"

 export default {
   name: 'Main',
   components: {
     Dashboard,
     Log,
     Submodule,
     Branch,
     Patch
   },
   props: {
   },
   data() {
     return {
       navbarHeight: "40px",
       navItems: ["Dashboard", "Log", "Submodule", "Branch", "Patch"],
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
       logInfo: [],
       submoduleInfo: [],
       branchInfo: [],
       pyobject: null
     }
   },
   mounted() {
     window.init = this.init;
     window.changePage = this.changePage;
     window.updateLogInfo = this.updateLogInfo;
     window.updateSubmoduleInfo = this.updateSubmoduleInfo;
     window.updateBranchInfo = this.updateBranchInfo;

     let that = this;
     window.addEventListener('keydown', function(event) {
       var event_key = event.key;

       if (event_key === "1") {
         that.changePage("Dashboard");
       } else if (event_key === "2") {
         that.changePage("Log");
       } else if (event_key === "3") {
         that.changePage("Submodule");
       } else if (event_key === "4") {
         that.changePage("Branch");
       } else if (event_key === "5") {
         that.changePage("Patch");
       }

       if (that.navCurrentItem === "Dashboard") {
         if (event_key === "m") {
           window.pyobject.copy_change_files_to_mirror_repo();
         } else if (event_key === "j") {
           that.$root.$emit("statusSelectNext");
         } else if (event_key === "k") {
           that.$root.$emit("statusSelectPrev");
         } else if (event_key === "s") {
           that.$root.$emit("statusStageFile");
         } else if (event_key === "d") {
           that.$root.$emit("statusDeleteFile");
         } else if (event_key === "c") {
           that.$root.$emit("statusCommitStage");
         } else if (event_key === "C") {
           that.$root.$emit("statusCommitAll");
         }
       } else if (that.navCurrentItem === "Log") {
         if (event_key === "j") {
           that.$root.$emit("logSelectNext");
         } else if (event_key === "k") {
           that.$root.$emit("logSelectPrev");
         } else if (event_key === "J") {
           that.$root.$emit("logSelectLast");
         } else if (event_key === "K") {
           that.$root.$emit("logSelectFirst");
         } else if (event_key === "Enter") {
           that.$root.$emit("logViewDiff");
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
          repoPath, repoHeadName, repoLastCommitId, repoLastCommitMessage) {
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
     },

     updateLogInfo(logInfo) {
       this.logInfo = logInfo;
     },

     updateSubmoduleInfo(submoduleInfo) {
       this.submoduleInfo = submoduleInfo;
     },

     updateBranchInfo(branchInfo) {
       this.branchInfo = branchInfo;
     }
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
</style>
