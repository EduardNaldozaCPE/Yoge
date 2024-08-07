const liveFeed      = document.getElementById('live-feed');
const camSwitchBtn  = document.getElementById('live-camswitch');
const widgetScore   = document.getElementById('widget-score');
const userId        = sessionStorage.getItem('userId');
const sequenceId    = sessionStorage.getItem('sequenceId');

var currentDevice   = 0;
var glob_sessionId  = null;
var showFeed        = false;
var isRecording     = false;
var poseListState   = []; // { step:number, posename:string, score:number, weight:number }
var currentStep     = 0;
var currentScore    = 0.0;

const resetVars = () => {
    $("#pose-table").scrollTop(0);
}


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
    glob_sessionId = sessionId;
    console.log("SESSION ID: "+sessionId);
    
    // Get rows to the pose list and save each ID in poseListState
    landmarkerAPI.getPoses(sequenceId);
    landmarkerAPI.onPoses((data)=>{
        console.log(data);
        let poseIds = [];
        $("#pose-table-body").html("");
        for (let i = 0; i < data.length; i++) {
            let poseId = "poseScore-".concat(i+1);
            $("#pose-table-body").append(`
                <tr id="pose-${i+1}">
                    <td id="poseName-${i+1}">${data[i]["poseName"]}</td>
                    <td id="${poseId}" class="poseScore">-</td>
                </tr>
            `);
            poseIds.push(poseId);
        }
        for (let i=0; i<poseIds.length; i++) {
            poseListState.push({
                "step":poseIds[i],
                "poseName":data[i]["poseName"], 
                "score":-1,
                "weight":data[i]["wght"]
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
        console.log("onStatus: Success");
        liveFeed.style.opacity = 1;
        showFeed = true;
        camSwitchBtn.disabled = false;
        resetVars();
    },
    // Landmarker failed to run. Reset to DeviceID 0 then re-run.
    failCallback = ()=>{
        console.log("onStatus: Failed. Restarting...");
        liveFeed.style.opacity = 0.2;
        currentDevice = 0;
        landmarkerAPI.restart(device=currentDevice);
        camSwitchBtn.disabled = true;
    }
);

landmarkerAPI.onSessionDone(()=>{
    console.log("SESSION DONE");
    $("#finish-btn").removeAttr('disabled');
    let finalScore = 0;
    
    for (let i = 0; i < poseListState.length; i++) {
        finalScore += (poseListState[i].score * poseListState[i].weight);
    }
    finalScore = finalScore / 100;
    console.log(finalScore);
    
    landmarkerAPI.recordHistory(glob_sessionId, finalScore);
});

landmarkerAPI.onFrame((imgStr)=>{
    if (!showFeed) { return } 
    liveFeed.src = imgStr;
});

landmarkerAPI.onNextPose(()=>{
    if (currentStep > 0) {
        poseListState[currentStep-1].score = currentScore;
    }
    $("#pose-table").scrollTop($("#pose-table").scrollTop()+30);
    currentStep++;
    console.log("currentStep = "+currentStep);
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
function returnToDashboard(page="dashboard") {
    landmarkerAPI.stop();
    electronWindow.transitionTo(`../dashboard/index.html?page=${page}`);
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