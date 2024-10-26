<script setup lang="ts">
  import { ref, Ref } from 'vue';
  import AppTitlebar from './components/AppTitlebar.vue';
  import AppSidebar from './components/AppSidebar.vue';
  import Home from './components/Home/Home.vue';

  type Page = "home" | "session" | "sequenes" | "scores";

  const currentPage : Ref<Page, Page> = ref('home');
  
</script>

<template>
  <AppTitlebar />
  <AppSidebar />
  <div id="main-content">
    <Home v-if="currentPage=='home'"></Home>
  </div>
</template>

<style scoped>
  #main-content {
    display: flex;
    padding: 40px;
    width: 100%;
    gap: 10px;
  }
</style>
