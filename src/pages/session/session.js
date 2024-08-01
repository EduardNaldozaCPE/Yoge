const liveFeed = document.getElementById('live-feed');
const camSwitchBtn = document.getElementById('live-camswitch');
const widgetScore = document.getElementById('widget-score');
var currentDevice = 0;
var showFeed = false;
var isRecording = false;
var poseListState = []; // {step:number, posename:string, score:number}
var currentStep = 0;
var currentScore = 0.0;

const userId = sessionStorage.getItem('userId');
const sequenceId = sessionStorage.getItem('sequenceId');

if (sequenceId == "undefined" || sequenceId == null) {
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
    console.log("SESSION ID: "+sessionId);
    
    // Get rows to the pose list and save each ID in poseListState
    landmarkerAPI.getPoses(sequenceId);
    landmarkerAPI.onPoses((data)=>{
        console.log(data);
        let poseIds = [];
        $("#pose-table-body").html("");;
        for (let i = 0; i < data.length; i++) {
            let poseId = "poseScore-".concat(i+1);
            $("#pose-table-body").append(`
                <tr id="pose-${i+1}">
                    <td id="poseName-${i+1}">${data[i]["poseName"]}</td>
                    <td id="${poseId}">-</td>
                </tr>
            `);
            poseIds.push(poseId);
        }
        for (let i=0; i<poseIds.length; i++) {
            poseListState.push({
                "step":poseIds[i],
                "poseName":data[i]["poseName"], 
                "score":-1
            });
        }
    });
});

landmarkerAPI.enableRestart(userId, sequenceId, ()=>{
    console.log("Rerunning landmarker...");
});

setInterval(() => {
    if (isRecording) landmarkerAPI.getScore();
}, 1000);

landmarkerAPI.onScore((data) => {
    let joints = ["leftElbow", "rightElbow", "leftKnee", "rightKnee", "leftShoulder", "rightShoulder", "leftHip", "rightHip"];
    let totalScore = 0.0;
    try {
        // Average all joints' scores. (TODO: Account for score weights)
        for (let i=0; i<joints.length; i++) {
            totalScore += data[joints[i]];
            totalScore = totalScore/joints.length;
        }
    } catch (e) {
        if (e instanceof TypeError) return;
        else console.log(e);
    }

    // Show the score in the widget
    currentScore = totalScore.toFixed(2);
    $(widgetScore).text(`${totalScore.toFixed(2)}%`);

    // Show the score in the pose-list table row
    if (currentStep > 0) {
        $("#"+poseListState[currentStep-1].step).text(currentScore);
    }
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
        landmarkerAPI.restart(device=currentDevice);
        camSwitchBtn.disabled = true;
    }
);

landmarkerAPI.onFrame((imgStr)=>{
    if (!showFeed) { return } 
    liveFeed.src = imgStr;
});

landmarkerAPI.onNextPose(()=>{
    currentStep++;
    console.log("currentStep = "+currentStep);
});

// landmarkerAPI.onSequenceFinish(()=>{
//     currentStep++;
// });

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