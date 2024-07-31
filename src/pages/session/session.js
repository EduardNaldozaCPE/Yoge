const liveFeed = document.getElementById('live-feed');
const camSwitchBtn = document.getElementById('live-camswitch');
const widgetScore = document.getElementById('widget-score');
var currentDevice = 0;
var showFeed = false;
var isRecording = false;
var poseScores = [];
var currentScore = 0.0;

const userId = sessionStorage.getItem('userId');
const sequenceId = sessionStorage.getItem('sequenceId');

if (sequenceId == "undefined" || sequenceId == undefined) {
    alert("Sequence Is undefined. Returning to dashboard...");
    returnToDashboard();
} else {
    landmarkerAPI.run(
        parseInt( userId ), 
        parseInt( sequenceId ), 
        device = currentDevice
    );
}

landmarkerAPI.onSession((sessionId)=>{
    // Run the landmarker, enable restart, and handle connection statuses
    console.log("SESSION ID: "+sessionId);
    landmarkerAPI.getPoses(sequenceId);
    landmarkerAPI.onPoses((data)=>{
        console.log(data);
        $("#pose-table-body").html("");
        for (let i = 0; i < data.length; i++) {
            $("#pose-table-body").append(`
                <tr>
                    <td>${data[i]["poseName"]}</td>
                    <td>--</td>
                </tr>
                `);
        }
    });

    landmarkerAPI.enableRestart(()=>{
        console.log("Rerunning landmarker...");
    });

    setInterval(() => {
        if (isRecording) landmarkerAPI.getScore();
    }, 1000);

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
            landmarkerAPI.restart(device=currentDevice);
            camSwitchBtn.disabled = true;
        }
    );

    landmarkerAPI.onFrame((imgStr)=>{
        if (!showFeed) { return } 
        liveFeed.src = imgStr;
    });

    landmarkerAPI.onNextPose(()=>{
        console.log('nextpose');
    });

    landmarkerAPI.onScore((data) => {
        let joints = ["leftElbow", "rightElbow", "leftKnee", "rightKnee", "leftShoulder", "rightShoulder", "leftHip", "rightHip"];
        let totalScore = 0.0;
        try {
            for (let i=0; i<joints.length; i++) {
                totalScore += data[joints[i]];
                totalScore = totalScore/joints.length;
            }
            widgetScore.innerText = `${totalScore.toFixed(2)}%`;
            currentScore = totalScore.toFixed(2);
        } catch (e) {
            if (e instanceof TypeError) return;
            else console.log(e);
        }
    });
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

/**
 * Stops the landmarker module and move back to dashboard
 */
function returnToDashboard() {
    landmarkerAPI.stop();
    electronWindow.transitionTo('../dashboard/index.html?page=dashboard');
}

/**
 * Handle Pause/Play button.
 */
function togglePlay() {
    if (isRecording){
        landmarkerAPI.pause();
    } else {
        landmarkerAPI.play();
    }
    isRecording = !isRecording
}