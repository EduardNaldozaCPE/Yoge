declare interface Poses {
    poseId: number,
    sequenceId: number,
    stepNum: number,
    poseName: string,
    targetLeftElbow: number,
    targetRightElbow: number,
    targetLeftKnee: number,
    targetRightKnee: number,
    targetLeftShoulder: number,
    targetRightShoulder: number,
    targetLeftHip: number,
    targetRightHip: number,
    duration: number,
    wght: number
}

declare interface Score {
    scoreId       : number,
    sessionId     : number,
    step          : number,
    leftElbow     : number, 
    rightElbow    : number, 
    leftKnee      : number, 
    rightKnee     : number, 
    leftShoulder  : number, 
    rightShoulder : number, 
    leftHip       : number, 
    rightHip      : number
}

declare type StatusType = "success"|"fail"|"empty"