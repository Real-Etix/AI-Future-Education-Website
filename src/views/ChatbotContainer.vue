/* create a container for the home page in order to 
use keep the chatbot in separate files and use the sidebar */

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import Chatbot from './Chatbot.vue'
</script>

<template>
    <Sidebar head="Vicuna"/>
    <div class="main">
      <Chatbot />
    </div>
</template>

<style scoped>
</style>
