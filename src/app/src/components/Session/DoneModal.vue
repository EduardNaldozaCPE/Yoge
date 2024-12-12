<script setup lang="ts">
    const props = defineProps(['score']);
</script>

<template>
    <div id="blackout-bg">
        <div id="modal-content">
            <h3>Good Job!</h3>
            <h1 id="modal-score">{{ props.score }}%</h1>
            <button id="return-btn" @click="$emit('finish')">Return To Dashboard</button>
        </div>
    </div>
</template>

<style scoped>
    #blackout-bg {
        height: 100%;
        width: 100%;
        background: #0007;
        position: fixed;
        margin: 0px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    #modal-content {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        min-width: 600;
        min-height: 400;
        background-color: #161616;
        padding: 50px;
        border-radius: 10px;

        h3 { margin-bottom: 0px; }
        h1 { margin: 20px; }
    }

    #return-btn {
        color: white;
        background-color: #222222;
        border-radius: 10px;
        border: 1px #5553;
    }
</style>