"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.response2PoseRecord = response2PoseRecord;
/**
 * Filters and formats necessary Pose Record data.
 * @param status Status of the ...
 * @param data Array of Score data
 * @param poses Array of Pose Data
 * @returns Final Array of pose data in PoseRecord format
 */
function response2PoseRecord(data, poses) {
    const finalData = [];
    // Set the template for the final data.
    for (let i = 0; i < poses.length; i++) {
        finalData.push({
            poseName: poses[i].poseName,
            latestScore: 0,
            bestScore: 0,
            avgScore: 0,
        });
    }
    // Go through each record and update the latest and best, and add up scores to be averaged afterwards
    for (let i = 0; i < data.length; i++) {
        // Set the latest score
        let latestscore = (data[i].leftElbow + data[i].rightElbow + data[i].leftKnee + data[i].rightKnee + data[i].leftShoulder + data[i].rightShoulder + data[i].leftHip + data[i].rightHip) / 8;
        finalData[data[i].step - 1].latestScore = latestscore;
        // Set the best score if the latest score is greater than the current best score
        if (latestscore > finalData[data[i].step - 1].bestScore)
            finalData[data[i].step - 1].bestScore = latestscore;
        // Sum up all the scores for averaging
        finalData[data[i].step - 1].avgScore = finalData[data[i].step - 1].avgScore + latestscore;
    }
    // Go through all the steps and average out the scores
    for (let i = 0; i < finalData.length; i++) {
        finalData[i].avgScore = finalData[i].avgScore / poses.length;
    }
    return finalData;
}
;
