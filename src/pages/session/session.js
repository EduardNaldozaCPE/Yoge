const liveFeed = document.getElementById('live-feed');
electronAPI.runConsumer();


function returnToDashboard() {
    electronAPI.stopConsumer();
    electronAPI.transitionTo('../dashboard/index.html?page=dashboard');
}

electronAPI.currentFrame((imgStr)=>{
    liveFeed.src = imgStr;
});