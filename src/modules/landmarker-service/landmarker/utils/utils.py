import math
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

# Format angle score to an insert query
def formatResult(sessionId, scores, timestamp) -> str:
    # print(f"Recording Score @ {timestamp}", file=sys.stderr)
    try:
        return f"""
            INSERT INTO score (sessionId, timestmp, leftElbow, rightElbow, leftKnee, rightKnee, leftShoulder, rightShoulder, leftHip, rightHip) VALUES 
                (
                {sessionId},
                {timestamp}, 
                {scores["left-elbow"]}, 
                {scores["right-elbow"]}, 
                {scores["left-knee"]}, 
                {scores["right-knee"]}, 
                {scores["left-shoulder"]}, 
                {scores["right-shoulder"]}, 
                {scores["left-hip"]}, 
                {scores["right-hip"]}
                );
            """
    except Exception as e:
        print("Error Occurred while recording score:", e , file=sys.stderr)


# Draw landmarks into cv image from landmarks 
def drawLandmarks(
        cv_frame, 
        img_size:tuple, 
        landmarks:dict, 
        targets:dict, 
        bestColour:tuple=(0,255,0), 
        worstColour:tuple=(50,0,200)
        ) -> tuple:
    
    next_frame = cv_frame

    # Get the angles for each listed joint.
    joints = {
        "elbow":    ["wrist", "shoulder"], 
        "shoulder": ["elbow", "hip"],
        "hip":      ["shoulder", "knee"],
        "knee":     ["hip", "ankle"]
        }
    
    angles = {}
    for joint in joints:
        angles[f"left-{joint}"] = _angleFrom3Points(
            ( landmarks[f"left-{joints[joint][0]}"].x,   landmarks[f"left-{joints[joint][0]}"].y ),
            ( landmarks[f"left-{joint}"].x,              landmarks[f"left-{joint}"].y ),
            ( landmarks[f"left-{joints[joint][1]}"].x,   landmarks[f"left-{joints[joint][1]}"].y ),
            )
        angles[f"right-{joint}"] = _angleFrom3Points(
            ( landmarks[f"right-{joints[joint][0]}"].x,  landmarks[f"right-{joints[joint][0]}"].y ),
            ( landmarks[f"right-{joint}"].x,             landmarks[f"right-{joint}"].y ),
            ( landmarks[f"right-{joints[joint][1]}"].x,  landmarks[f"right-{joints[joint][1]}"].y ),
            )
    
    # Calculate score for each angle, then draw landmarks
    scores = {}
    for key in landmarks:
        if key == "left-wrist": break
        score = _scoreFromAngles(angles[key], targets[key])
        scores[key] = score

        try:
            next_frame = cv.circle(
                cv_frame,
                (
                    int(landmarks[key].x * img_size[0] * 2), 
                    int(landmarks[key].y * img_size[1] * 2)
                ),
                20, _colourFromScore(score, bestColour, worstColour), 8, 2, 1 )
        except IndexError:
            print(f"Landmark {key} Not in array. Skipping.", file=sys.stderr)

    next_frame = cv.putText(
        cv_frame, str(targets),
        ( 10, 10 ), cv.FONT_HERSHEY_COMPLEX_SMALL, 1,
        (200,200,0), 1, cv.LINE_AA, False)

    return (scores, next_frame)

# Calculate the angle between 3 points
def _angleFrom3Points(p1:tuple, p2:tuple, p3:tuple) -> float:
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    angle = math.degrees(math.atan2(y3-y2, x3-x2) - math.atan2(y1-y2, x1-x2))
    if angle < 0: angle += 360
    return angle

# Calculate the score from angles, accounting for the angle's orientation
def _scoreFromAngles(angle:float, target:float) -> float:
    target_90cc = target - 90   # 90 degrees counter-clockwise of target angle 
    target_90c = target + 90    # 90 degrees clockwise of target angle 

    # If the target_90cc is below 0, wrap the angle and include scores for angles below 0
    if target_90cc < 0:
        target_90cc += 360
        # if angle is within the normal range between 0 to target angle
        if 0 < angle <= target:
            return int(100-((abs(angle - target)/90)*100))
        # if angle is within the normal range between target angle to target_90c
        elif target <= angle < target_90c:
            return int(100-((abs(angle - target)/90)*100))
        # if angle is within the extended range between target_90cc to 0 to target angle
        elif target_90cc < angle < 360: 
            return int(100-(((target-(angle-360))/90)*100))
        # if angle is not within scoring range
        else: return 0 
            
    # If the target_90c is above 360, wrap the angle and include scores for angles above 360 
    elif target_90c > 360:
        target_90c -= 360
        # if angle is within the normal range between target angle to 360
        if target <= angle < 360:
            return int(100-((abs(angle - target)/90)*100))
        # if angle is within the normal range between target_90cc to target angle 
        if target_90cc < angle <= target:
            return int(100-((abs(angle - target)/90)*100))
        # if angle is within the extended range between target angle to 0 to target_90c 
        if 0 < angle < target_90c:
            return int(100-((abs(target-(angle+360))/90)*100)) 
        # if angle is not within scoring range
        else: return 0 
    
    else:
        if target <= angle < target_90c:
            return int(100-((abs(angle - target)/90)*100))
        if target_90cc < angle <= target:    
            return int(100-((abs(angle - target)/90)*100))
        else:
            return 0
    
# Linearly interpolate rgb between best and worst colours depending on the score
def _colourFromScore(score:float, bestColour:tuple, worstColour:tuple) -> tuple:
    return (
        worstColour[0]+(score/100.0)*(bestColour[0]-worstColour[0]),
        worstColour[1]+(score/100.0)*(bestColour[1]-worstColour[1]),
        worstColour[2]+(score/100.0)*(bestColour[2]-worstColour[2]),
        )