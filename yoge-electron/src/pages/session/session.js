const liveFeed = document.getElementById('live-feed');
electronAPI.runConsumer();

electronAPI.currentFrame((imgStr)=>{liveFeed.src = imgStr;});