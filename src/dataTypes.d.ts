export type landmarkerCommand = "PLAY" | "PAUSE";

export interface config {
    MODEL_PATH      : string,
    DB_PATH         : string,
    LANDMARKER_PATH : string,
    FRAMEWIDTH      : number,
    FRAMEHEIGHT     : number
}


export interface scoreType {
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
export type scoreKey = keyof scoreType;

export interface sequenceType {
    sequenceId    : number,
    sequenceName  : string,
    poseNum       : number,
    tags          : string,
    difficulty    : string,
}
export type sequenceKey = keyof sequenceType;


export interface sessionType {
    sessionId   : number,
    userId  : number,
    sequenceId  : number,
}
export type sessionKey = keyof sessionType;