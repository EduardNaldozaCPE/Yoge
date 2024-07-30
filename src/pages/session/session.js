const liveFeed = document.getElementById('live-feed');
const camSwitchBtn = document.getElementById('live-camswitch');
const widgetScore = document.getElementById('widget-score');
let currentDevice = 0;
let showFeed = false;
let isPlaying = false;
var poseScores = [];
var currentScore = 0.0;

const userId = sessionStorage.getItem('userId');
const sequenceId = sessionStorage.getItem('sequenceId');
var isSessionValid = false;

if (userId !== undefined || sequenceId !== undefined) {
    isSessionValid = true;
    console.log(userId);
    console.log(sequenceId);
    landmarkerAPI.run(userId, sequenceId, device=currentDevice);
}

if (isSessionValid) {
    // Run the landmarker, enable restart, and handle connection statuses
    landmarkerAPI.getPoses(sessionId, (data)=>{
        console.log(data);
    });

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
            landmarkerAPI.restart(device=currentDevice);
            camSwitchBtn.disabled = true;
        }
    );

    landmarkerAPI.onFrame((imgStr)=>{
        if (!showFeed) { return } 
        liveFeed.src = imgStr;
    });

    setInterval(() => {
        landmarkerAPI.getScore();
    }, 1000);

    landmarkerAPI.onNextPose(()=>{
        console.log('nextpose');
    });

    landmarkerAPI.onScore((data) => {
        let joints = ["leftElbow", "rightElbow", "leftKnee", "rightKnee", "leftShoulder", "rightShoulder", "leftHip", "rightHip"];
        let totalScore = 0.0;
        try {
            for (let i=0; i<joints.length; i++) {
                console.log(data[joints[i]]);
                totalScore += data[joints[i]];
                totalScore = totalScore/joints.length;
            }
            widgetScore.innerText = `${totalScore.toFixed(2)}%`;
            currentScore = totalScore.toFixed(2);
        } catch (e) {
            if (e === TypeError) return;
            else console.log(e);
        }
    });

}

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

function togglePlay() {
    if (isPlaying){
        landmarkerAPI.pause();
    } else {
        landmarkerAPI.play();
    }
    isPlaying = !isPlaying
}