"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
const liveFeed = document.getElementById('live-feed');
const camSwitchBtn = document.getElementById('live-camswitch');
const widgetScore = document.getElementById('widget-score');
const userId = sessionStorage.getItem('userId');
const sequenceId = sessionStorage.getItem('sequenceId');
var showFeed = false;
var isRecording = false;
var currentDevice = 0;
var glob_sessionId = -1;
var currentStep = 0;
var currentScore = "0.0";
var poseListState = [];
const resetVars = () => $("#pose-table").scrollTop(0);
if (sequenceId == "undefined" || sequenceId == null) {
    alert("Sequence Is undefined. Returning to dashboard...");
    returnToDashboard();
}
else {
    window.landmarkerAPI.run(parseInt(userId), parseInt(sequenceId), currentDevice);
}
window.landmarkerAPI.onSession((sessionId) => __awaiter(void 0, void 0, void 0, function* () {
    glob_sessionId = sessionId;
    console.log("SESSION ID: " + sessionId);
    yield _getPoses();
}));
// Get rows to the pose list and save each ID in poseListState
function _getPoses() {
    return __awaiter(this, void 0, void 0, function* () {
        let poses = yield window.landmarkerAPI.getPoses(parseInt(sequenceId));
        let poseIds = [];
        console.log(poses);
        $("#pose-table-body").html("");
        for (let i = 0; i < poses.length; i++) {
            let poseId = "poseScore-".concat((i + 1).toString());
            $("#pose-table-body").append(`
            <tr id="pose-${i + 1}">
                <td id="poseName-${i + 1}">${poses[i]["poseName"]}</td>
                <td id="${poseId}" class="poseScore">-</td>
            </tr>
        `);
            poseIds.push(poseId);
        }
        for (let i = 0; i < poseIds.length; i++) {
            poseListState.push({
                step: poseIds[i],
                poseName: poses[i]["poseName"],
                score: -1,
                weight: poses[i]["wght"]
            });
        }
    });
}
window.landmarkerAPI.enableRestart(parseInt(userId), parseInt(sequenceId), () => {
    console.log("Rerunning landmarker...");
});
setInterval(() => __awaiter(void 0, void 0, void 0, function* () {
    if (!isRecording)
        return;
    let score = yield window.landmarkerAPI.getScore();
    let joints = ["leftElbow", "rightElbow", "leftKnee", "rightKnee", "leftShoulder", "rightShoulder", "leftHip", "rightHip"];
    let totalScore = 0.0;
    try {
        // Average all joints' scores. (TODO: Account for score weights)
        for (let [key, value] of Object.entries(score)) {
            if (joints.includes(key)) {
                totalScore += value;
                totalScore = totalScore / joints.length;
            }
        }
    }
    catch (e) {
        if (e instanceof TypeError)
            return;
        else
            console.log(e);
    }
    // Show the score in the widget
    currentScore = totalScore.toFixed(2);
    $(widgetScore).text(`${totalScore.toFixed(2)}%`);
    // Show the score in the pose-list table row
    if (currentStep > 0) {
        $("#" + poseListState[currentStep - 1].step).text(currentScore);
    }
}), 1000);
window.landmarkerAPI.onStatus(
// Landmarker ran successfully. Show the feed.
() => {
    console.log("onStatus: Success");
    liveFeed.style.opacity = "1";
    showFeed = true;
    camSwitchBtn.removeAttribute("disabled");
    resetVars();
}, 
// Landmarker failed to run. Reset to DeviceID 0 then re-run.
() => {
    console.log("onStatus: Failed. Restarting...");
    liveFeed.style.opacity = "0.2";
    currentDevice = 0;
    window.landmarkerAPI.restart(parseInt(userId), parseInt(sequenceId), currentDevice);
    camSwitchBtn.setAttribute("disabled", "true");
});
window.landmarkerAPI.onSessionDone(() => {
    console.log("SESSION DONE");
    $("#finish-btn").removeAttr('disabled');
    let finalScore = 0;
    for (let i = 0; i < poseListState.length; i++) {
        finalScore += (poseListState[i].score * poseListState[i].weight);
    }
    finalScore = finalScore / 100;
    console.log(finalScore);
    localStorage.setItem('lastSequenceId', sequenceId);
    window.landmarkerAPI.recordHistory(glob_sessionId, finalScore);
});
window.landmarkerAPI.onFrame((imgStr) => {
    if (!showFeed) {
        return;
    }
    liveFeed.setAttribute("src", imgStr);
});
window.landmarkerAPI.onNextPose(() => {
    if (currentStep > 0) {
        poseListState[currentStep - 1].score = parseFloat(currentScore);
    }
    let poseTable = $("#pose-table");
    let currentScrollTop = poseTable.scrollTop();
    poseTable.scrollTop(currentScrollTop + 30);
    currentStep++;
    console.log("currentStep = " + currentStep);
});
/**
 * Restart the landmarker process. Wait for new landmarker via OnStatus()
 */
function switchCamera() {
    camSwitchBtn.setAttribute("disabled", "true");
    liveFeed.setAttribute("src", "../..assets/loading.png");
    showFeed = false;
    liveFeed.style.opacity = "0.2";
    currentDevice++;
    window.landmarkerAPI.restart(parseInt(userId), parseInt(sequenceId), currentDevice);
}
/**
 * Stops the landmarker module and move back to dashboard
 */
function returnToDashboard(page = "dashboard") {
    window.landmarkerAPI.stop();
    window.electronWindow.transitionTo(`../dashboard/index.html?page=${page}`);
}
/**
 * Handle Pause/Play button.
 */
function togglePlay() {
    if (isRecording) {
        window.landmarkerAPI.pause();
    }
    else {
        window.landmarkerAPI.play();
    }
    isRecording = !isRecording;
}
