<script src="@/assets/js/app">
</script>

<template>
 <Sidebar head="Vicuna" :userID = 'userID' v-if="renderSidebar"/>
 <div class="main">
    <router-view :userID = 'userID' @show-sidebar="login" @update-chat="forceRerender"/>
 </div>
</template>

<style lang="scss" scoped>
</style>
