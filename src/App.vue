<script src="@/assets/js/app">
</script>

<template>
 <Sidebar head="Vicuna" :userID = 'userID' v-if="!isOnSpecificPage || rendereSidebar"/>
 <div class="main">
    <router-view :userID = 'userID' @update-chat-list="forceRerender"/>
 </div>
</template>

<style lang="scss" scoped>
</style>
