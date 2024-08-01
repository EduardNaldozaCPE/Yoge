import math, sys
import cv2 as cv
from .utils import *
from landmarker.Joints import *

def formatResult(sessionId, scores, step) -> str:
    """ Format angle score to an insert query """
    try:
        return f"""
            INSERT INTO score (sessionId, step, leftElbow, rightElbow, leftKnee, rightKnee, leftShoulder, rightShoulder, leftHip, rightHip) VALUES 
                (
                {sessionId},
                {step}, 
                {scores[Joint.leftElbow]}, 
                {scores[Joint.rightElbow]}, 
                {scores[Joint.leftKnee]}, 
                {scores[Joint.rightKnee]}, 
                {scores[Joint.leftShoulder]}, 
                {scores[Joint.rightShoulder]}, 
                {scores[Joint.leftHip]}, 
                {scores[Joint.rightHip]}
                );
            """
    except Exception as e:
        print("Error Occurred while recording score:", e , file=sys.stderr)
        return ""


def calculateScores( landmarks:JointLandmark, targets:JointFloat ):
    """ Get the angles for each listed joint, then Calculate the scores """
    # Get the angles for each listed joint.
    jointNeighbours = {
        "Elbow":    ["Wrist", "Shoulder"],
        "Shoulder": ["Elbow", "Hip"],
        "Hip":      ["Shoulder", "Knee"],
        "Knee":     ["Hip", "Ankle"]
        }
    
    angles = JointFloat("angles")
    for joint in jointNeighbours:
        try:
            angles.set(Joint[f"left{joint}"], __angleFrom3Points(
                ( 
                    landmarks.get(Joint[f"left{jointNeighbours[joint][0]}"]).x,
                    landmarks.get(Joint[f"left{jointNeighbours[joint][0]}"]).y ),
                (
                    landmarks.get(Joint[f"left{joint}"]).x,
                    landmarks.get(Joint[f"left{joint}"]).y ),
                ( 
                    landmarks.get(Joint[f"left{jointNeighbours[joint][1]}"]).x,
                    landmarks.get(Joint[f"left{jointNeighbours[joint][1]}"]).y )
                ))
            angles.set(Joint[f"right{joint}"], __angleFrom3Points(
                (
                    landmarks.get(Joint[f"right{jointNeighbours[joint][0]}"]).x,
                    landmarks.get(Joint[f"right{jointNeighbours[joint][0]}"]).y ),
                (
                    landmarks.get(Joint[f"right{joint}"]).x,
                    landmarks.get(Joint[f"right{joint}"]).y ),
                (
                    landmarks.get(Joint[f"right{jointNeighbours[joint][1]}"]).x,
                    landmarks.get(Joint[f"right{jointNeighbours[joint][1]}"]).y )
                ))
        except Exception as e:
            print("Error while getting angles:", e, file=sys.stderr)
    
    # Calculate score for each angle
    scores = JointFloat("scores")
    for key in landmarks.getKeys():
        if key == Joint.leftWrist: break
        try:
            scores.set( key, __scoreFromAngles(angles.get(key),targets.get(key)) )
        except Exception as e:
            print("Error while calculating scores", e, file=sys.stderr)
    
    return scores
    

def drawLandmarks(
        cv_frame, 
        img_width:int, 
        img_height:int, 
        landmarks:JointLandmark, 
        scores:JointFloat, 
        bestColour:tuple=(0,255,0), 
        worstColour:tuple=(50,0,200)
        ):
    """ Draw landmarks into cv image from landmarks """
    
    next_frame = cv_frame
    
    # Calculate score for each angle, then draw landmarks
    for key in landmarks.getKeys():
        if key == Joint.leftWrist: break
        try:
            next_frame = cv.circle(
                cv_frame,
                (
                    int(landmarks.get(key).x * img_width * 2), 
                    int(landmarks.get(key).y * img_height * 2)
                ),
                20, __colourFromScore(scores.get(key), bestColour, worstColour), 8, 2, 1 )
        except IndexError:
            print(f"Landmark {key} Not in array. Skipping.", file=sys.stderr)
        except Exception as e:
            print("Error while drawing circle Landmarks", e, file=sys.stderr)

    return next_frame


def __angleFrom3Points(p1:tuple, p2:tuple, p3:tuple) -> float:
    """ Calculate the angle between 3 points """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    angle = math.degrees(math.atan2(y3-y2, x3-x2) - math.atan2(y1-y2, x1-x2))
    if angle < 0: angle += 360
    return angle


def __scoreFromAngles(angle:float, target:float) -> float:
    """ Calculate the score from angles, accounting for the angle's orientation """
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
    

def __colourFromScore(score:float, bestColour:tuple, worstColour:tuple) -> tuple:
    """ Linearly interpolate rgb between best and worst colours depending on the score """
    return (
        worstColour[0]+(score/100.0)*(bestColour[0]-worstColour[0]),
        worstColour[1]+(score/100.0)*(bestColour[1]-worstColour[1]),
        worstColour[2]+(score/100.0)*(bestColour[2]-worstColour[2]),
        )