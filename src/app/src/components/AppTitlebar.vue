<script setup lang="ts">
</script>

<template>
    <div id="app-title-bar">
        <div id="app-draggable">
            <h5 id="app-title">Yoge</h5>
        </div>
        <div id="app-trafficlights">
            <button class="app-trafficlight" id="btn-minimise" onclick="electronWindow.windowMinimize()">&#128469;</button>
            <button class="app-trafficlight" id="btn-maximise" onclick="electronWindow.windowMaximize()">&#128470;</button>
            <button class="app-trafficlight" id="btn-close" onclick="electronWindow.windowClose()">&#10006;</button>
        </div>
    </div>
</template>

<style scoped>
    #app-title-bar {
        min-height: 21px;
        max-height: 21px;
        min-width: 100dvw;

        position: fixed;
        border-bottom: #262626 1px solid;
        top: 0px;
        left: 0px;
        right: 0px;
        background: #232323;

        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }
    #app-draggable {
        -webkit-app-region: drag;
        width: 100%;
    }

    #app-title-bar h5 {
        margin: 0px 0px 0px 10px;
        font-weight: 400;
        color: #555;
    }
    #app-trafficlights {
        padding: 0px;
        min-height: 20px;
        max-height: 20px;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
    }
    
    .app-trafficlight {
        min-height: inherit;
        max-height: inherit;
        min-width: 30px;
        background: #1a1a1a;
        color: #555;
        font-size: 8px;
        font-weight: bold;
        border: 1px #222 solid;
        border-radius: 2px;
        margin-left: 2px;
    }

    
    .app-trafficlight:hover {
        background: #2f2f2f;
    }

    .app-trafficlight:active {
        background: #2f2f2f;
    }
</style>