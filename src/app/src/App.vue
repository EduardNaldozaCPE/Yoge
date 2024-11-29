<script setup lang="ts">
  import { ref, Ref } from 'vue';
  import AppTitlebar from './components/AppTitlebar.vue';
  import AppSidebar from './components/AppSidebar.vue';
  import Home from './components/Dashboard/Home.vue';
  import Sequences from './components/Dashboard/Sequences.vue';
  import Session from './components/Session/Session.vue';

  type Page = "dashboard" | "session";
  type Content = "home" | "sequences" | "scores";

  interface SessionDetails {
    userId: number,
    sequenceId: number,
    sessionId: number,
    currentDevice: number,
  }

  const currentPage : Ref<Page> = ref('dashboard');
  const currentContent : Ref<Content> = ref('home');
  const sessionDetails : Ref<SessionDetails> = ref({
    userId: 0,
    sequenceId: -1,
    sessionId: -1,
    currentDevice: 0
  });

  async function startSession(selectedSequenceId:number) {
    if (selectedSequenceId == -1)
      return alert('Please Select a Pose Sequence');
    if (sessionDetails.value.userId == -1)
      return alert('UserId not set');
    
    sessionDetails.value.sequenceId = selectedSequenceId;

    window.landmarkerAPI.run(
      sessionDetails.value.userId,
      sessionDetails.value.sequenceId,
      sessionDetails.value.currentDevice
    );
    
    window.landmarkerAPI.onSession(async (sId:number)=>{
      sessionDetails.value.sessionId = sId;
      console.log(sessionDetails.value.sessionId);
      currentPage.value = "session";
    });
  }

  function stopSession()  {
    window.landmarkerAPI.stop();
    currentPage.value = "dashboard"; 
  }
</script>

<template>
  <AppTitlebar />
  <AppSidebar v-if="currentPage=='dashboard'" :content="currentContent" @changeContent="(p) => currentContent = p"/>
  <div v-if="currentPage == 'dashboard'" id="main-content">
    <Home v-if="currentContent=='home'" @startSession="startSession" />
    <Sequences v-if="currentContent=='sequences'" @startSession="startSession" />
  </div>
  <Session v-if="currentPage == 'session'" id="main-content" @stopSession="stopSession" :sessionDetails="sessionDetails"/>

</template>

<style scoped>
  #main-content {
    display: flex;
    padding: 40px;
    width: 100%;
    gap: 10px;
  }
</style>
