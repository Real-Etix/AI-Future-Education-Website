<script src="@/assets/js/app">
</script>

<template>
  <Sidebar head="XXChatBot" :userID = 'userID' v-if="renderSidebar"/>
  <div class="main">
    <RouterView :userID = 'userID' @temp-update-chat="forceRerender"/>
  </div>
</template>

<style lang="scss" scoped>
</style>
