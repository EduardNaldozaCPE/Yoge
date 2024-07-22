import sys
import cv2 as cv 
import mediapipe as mp 

JOINT_IDS = {
    "leftShoulder"  : 11,
    "rightShoulder" : 12,
    "leftElbow"     : 13,
    "rightElbow"    : 14,
    "leftHip"       : 23,
    "rightHip"      : 24,
    "leftKnee"      : 25,
    "rightKnee"     : 26,
}

# Format a score to an insert query
def formatResult(sessionId, result, timestamp) -> str:
    # print(f"Recording Score @ {timestamp}", file=sys.stderr)

    filteredScore = {}
    if type(result) is not mp.tasks.vision.PoseLandmarkerResult: raise Exception("formatResult did not recieve a PoseLandmarkerResult")
    try:
        for key in JOINT_IDS:
            filteredScore[key] = {}
            filteredScore[key]['x'] = result.pose_landmarks[0][JOINT_IDS[key]].x
            filteredScore[key]['y'] = result.pose_landmarks[0][JOINT_IDS[key]].y
            filteredScore[key]['z'] = result.pose_landmarks[0][JOINT_IDS[key]].z

        return f"""
            INSERT INTO score (sessionId, timestamp, leftElbow, rightElbow, leftKnee, rightKnee, leftShoulder, rightShoulder, leftHip, rightHip) VALUES 
                (
                {sessionId},
                {timestamp}, 
                {filteredScore["leftElbow"]["x"]}, 
                {filteredScore["rightElbow"]["x"]}, 
                {filteredScore["leftKnee"]["x"]}, 
                {filteredScore["rightKnee"]["x"]}, 
                {filteredScore["leftShoulder"]["x"]}, 
                {filteredScore["rightShoulder"]["x"]}, 
                {filteredScore["leftHip"]["x"]}, 
                {filteredScore["rightHip"]["x"]}
                );
            """
    except IndexError as e:
        print("Landmarks incomplete. Skipping.", file=sys.stderr)
    except Exception as e:
        print("Error Occurred while recording score:", e , file=sys.stderr)

# Draw landmarks into cv image from landmarks 
def drawLandmarks(cv_frame, img_size:tuple, landmarks:dict):
    next_frame = cv_frame
    for key in landmarks:
        try:
            next_frame = cv.circle( 
                cv_frame,
                ( int(landmarks[key].x * img_size[0] * 2), int(landmarks[key].y * img_size[1] * 2) ),
                12, (200, 50, 200), 1, 1, 1 )
        except IndexError:
            print(f"Landmark \"{key}\" Not in array. Skipping.", file=sys.stderr)
            continue
    return next_frame