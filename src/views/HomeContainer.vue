/* create a container for the home page in order to 
use keep the home page in separate files and use the sidebar */
<script setup>
import Sidebar from '../components/Sidebar.vue'
import Home from './Home.vue'
</script>

<template>
  <Sidebar head="Vicuna"/>
  <div class="main">
    <Home />
  </div>
</template>

<style scoped>
</style>