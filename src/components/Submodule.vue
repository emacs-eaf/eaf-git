<template>
  <div class="box">
    <Dialog
      :backgroundColor="backgroundColor"
      :title="dialogTitle">
      <virtual-list
        v-if="submoduleInfo.length > 0"
        ref="submodulelist"
        class="list"
        :keeps="50"
        :estimate-size="100"
        :data-key="'index'"
        :data-sources="submoduleInfo"
        :data-component="submoduleItemComponent"/>
      <div
        v-else
        class="notify">
        No submodule found in current repository.
      </div>
    </Dialog>
  </div>
</template>

<script>
 import Dialog from "./Dialog.vue"
 import SubmoduleItem from './SubmoduleItem'
 import VirtualList from 'vue-virtual-scroll-list'

 import { keepSelectVisible, getListPageElementNumber, regsiterJsFunctions } from "./utils.js"

 export default {
   name: 'Submodule',
   components: {
     'virtual-list': VirtualList,
     Dialog
   },
   props: {
     submoduleInfo: Array,
     backgroundColor: String,
     selectColor: String,
     currentSubmoduleIndex: Number,
     searchSubmoduleKeyword: String,
     searchSubmoduleMatchNumber: Number,
     searchSubmoduleIndex: Number,
     pyobject: Object
   },
   data() {
     return {
       submoduleItemComponent: SubmoduleItem,
       currentPageElementNum: 0
     }
   },
   computed: {
     dialogTitle() {
       if (this.searchSubmoduleKeyword != "") {
         return "Submodule (" + this.submoduleInfo.length + ") [ Search '" + this.searchSubmoduleKeyword + "' " + (this.searchSubmoduleIndex + 1) + "/" + this.searchSubmoduleMatchNumber + " ]";
       } else {
         return "Submodule (" + this.submoduleInfo.length + ")";
       }
     }
   },
   watch: {
     currentSubmoduleIndex: {
       // eslint-disable-next-line no-unused-vars
       handler: function(val, oldVal) {
         if (this.submoduleInfo.length > 0) {
           keepSelectVisible(this.$refs.submodulelist, val);
         }
       }
     },
   },
   mounted() {
     var that = this;

     this.$root.$on("submodule_view", function () {
       that.pyobject.submodule_view(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });

     this.$root.$on("submodule_open", function () {
       that.pyobject.submodule_open(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });

     this.$root.$on("submodule_remove", function () {
       that.pyobject.submodule_remove(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });

     this.$root.$on("submodule_update", function () {
       that.pyobject.submodule_update(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });

     this.$root.$on("submodule_move", function () {
       that.pyobject.submodule_move(that.submoduleInfo[that.currentSubmoduleIndex].name);
     });

     this.$root.$on("submodule_rollback", function () {
       that.pyobject.submodule_rollback(that.submoduleInfo[that.currentSubmoduleIndex].name,
                                        that.submoduleInfo[that.currentSubmoduleIndex].head_id);
     });

     regsiterJsFunctions(this, ["submodule_select_pg_up", "submodule_select_pg_dn"]);
   },
   beforeDestroy() {
     this.$root.$off("submodule_view");
     this.$root.$off("submodule_open");
     this.$root.$off("submodule_remove");
     this.$root.$off("submodule_update");
     this.$root.$off("submodule_rollback");
     this.$root.$off("submodule_select_pg_up");
     this.$root.$off("submodule_select_pg_dn");
   },
   methods: {
     submoduleSelectPgUp() {
       this.$emit("updateSubmoduleIndex", this.currentSubmoduleIndex - getListPageElementNumber(this.$refs.submodulelist));
     },

     submoduleSelectPgDn() {
       this.$emit("updateSubmoduleIndex", this.currentSubmoduleIndex + getListPageElementNumber(this.$refs.submodulelist));
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
   display: flex;
   flex-direction: row;
   align-items: center;

   padding-left: 10px;
   padding-right: 10px;
   font-size: 16px;
   height: 30px;
 }

 .notify {
   display: flex;
   flex-direction: column;
   justify-content: center;

   height: 100%;

   font-size: 16px;
   text-align: center;
   justify-self: center;
   margin: auto;
   font-size: 20px;
 }

 .list {
   z-index: 100;
   overflow-y: scroll;
   height: 100%;
 }
</style>
