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
        {{ repoPath }} ({{ repoHeadName }}) [{{ repoLastCommitId }} {{ repoLastCommitMessage }}]
      </div>
    </div>
    <div
      class="page"
      :style="{ 'margin-top': navbarHeight }">
      <Dashboard v-if="navCurrentItem == 'Dashboard'"/>
      <Log
        v-if="navCurrentItem == 'Log'" 
        :logInfo="logInfo"
        :idColor="idColor"
        :dateColor="dateColor"
        :authorColor="authorColor"/>
      <Submodule
        v-if="navCurrentItem == 'Submodule'"
        :submoduleInfo="submoduleInfo"/>
      <Branch v-if="navCurrentItem == 'Branch'"/>
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
       submoduleInfo: []
     }
   },
   mounted() {
     window.init = this.init;
     window.changePage = this.changePage;
     window.updateLogInfo = this.updateLogInfo;
     window.updateSubmoduleInfo = this.updateSubmoduleInfo;
   },
   created() {
     // eslint-disable-next-line no-undef
     new QWebChannel(qt.webChannelTransport, channel => {
       window.pyobject = channel.objects.pyobject;
     });
   },
   methods: {
     init(backgroundColor, panelColor, textColor, navItemActiveColor, infoColor, 
          dateColor, idColor, authorColor,
          repoPath, repoHeadName, repoLastCommitId, repoLastCommitMessage) {
       this.backgroundColor = backgroundColor;
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
