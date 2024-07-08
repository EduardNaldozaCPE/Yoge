const liveFeed = document.getElementById('live-feed');
electronAPI.runConsumer();

electronAPI.checkConnection((isConnected)=>{
    console.log("isConnected: ", isConnected);
});

electronAPI.currentFrame((imgStr)=>{
    liveFeed.src = imgStr;
})