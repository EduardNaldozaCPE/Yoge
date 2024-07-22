const liveFeed = document.getElementById('live-feed');
const camSwitchBtn = document.getElementById('live-camswitch');
let currentDevice = 0;
let showFeed = false;

// Run the landmarker, enable restart, and handle connection statuses
landmarkerAPI.run(device=currentDevice);

landmarkerAPI.enableRestart(()=>{
    console.log("Rerunning landmarker...");
});

landmarkerAPI.onStatus(
    // Landmarker ran successfully. Show the feed.
    successCallback = ()=>{
        console.log("LANDMARKER RAN SUCCESSFULLY");
        liveFeed.style.opacity = 1;
        showFeed = true;
        camSwitchBtn.disabled = false;
    },
    // Landmarker failed to run. Reset to DeviceID 0 then re-run.
    failCallback = ()=>{
        console.log("LANDMARKER FAILED TO RUN");
        liveFeed.style.opacity = 0.2;
        currentDevice = 0;
        landmarkerAPI.run();
        camSwitchBtn.disabled = true;
    }
);

landmarkerAPI.onFrame((imgStr)=>{
    if (!showFeed) { return } 
    liveFeed.src = imgStr;
});

/**
 * Restart the landmarker process. Wait for new landmarker via OnStatus()  
 */
function switchCamera() {
    camSwitchBtn.disabled = true;
    liveFeed.src = "../../media/loading.png";
    showFeed = false;
    liveFeed.style.opacity = 0.2;
    currentDevice++;
    landmarkerAPI.restart(device=currentDevice);
}

function returnToDashboard() {
    landmarkerAPI.stop();
    electronWindow.transitionTo('../dashboard/index.html?page=dashboard');
}