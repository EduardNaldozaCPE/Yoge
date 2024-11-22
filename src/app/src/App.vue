<script setup lang="ts">
  import { ref, Ref } from 'vue';
  import AppTitlebar from './components/AppTitlebar.vue';
  import AppSidebar from './components/AppSidebar.vue';
  import Home from './components/Dashboard/Home.vue';
  import Sequences from './components/Dashboard/Sequences.vue';

  type Page = "dashboard" | "session";
  type Content = "home" | "sequences" | "scores";

  const currentPage : Ref<Page> = ref('dashboard');
  const currentContent : Ref<Content> = ref('home');

  function startSession() { currentPage.value = "session"; }
  function stopSession()  { currentPage.value = "dashboard"; }
</script>

<template>
  <AppTitlebar />
  <AppSidebar v-if="currentPage=='dashboard'" :content="currentContent" @changeContent="(p) => currentContent = p"/>
  <div v-if="currentPage == 'dashboard'" id="main-content">
    <Home v-if="currentContent=='home'" @startSession="startSession" />
    <Sequences v-if="currentContent=='sequences'" @startSession="startSession" />
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
