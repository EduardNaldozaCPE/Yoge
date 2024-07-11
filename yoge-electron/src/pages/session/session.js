const liveFeed = document.getElementById('live-feed');
electronAPI.runConsumer();

// TODO -- Re-open Named pipe on exit. To fix unsuccessful connections. (ie when camera is off)
//  Create a signal to stop connection from the client.
electronAPI.currentFrame((imgStr)=>{liveFeed.src = imgStr;});