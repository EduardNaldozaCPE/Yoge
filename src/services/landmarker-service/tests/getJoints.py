import sys
class Landmark:
    def __init__(self,x,y):
        self.x = x
        self.y = y

def main():
    landmarks = {
        "left-shoulder"  : Landmark(0.00, 0.00),
        "right-shoulder" : Landmark(0.00, 0.00),
        "left-elbow"     : Landmark(0.00, 0.00),
        "right-elbow"    : Landmark(0.00, 0.00),
        "left-hip"       : Landmark(0.00, 0.00),
        "right-hip"      : Landmark(0.00, 0.00),
        "left-knee"      : Landmark(0.00, 0.00),
        "right-knee"     : Landmark(0.00, 0.00),
        # Only used for calculations
        "left-wrist"    : Landmark(0.00, 0.00),
        "right-wrist"   : Landmark(0.00, 0.00),
        "left-ankle"    : Landmark(0.00, 0.00),
        "right-ankle"   : Landmark(0.00, 0.00)
    }

    joints = {
        "elbow": ["wrist", "shoulder"],
        "shoulder": ["elbow", "hip"],
        "hip": ["shoulder", "knee"],
        "knee": ["hip", "ankle"]
        }

    angles = {}
    # print(landmarks[joints["elbow"][0]])

    for joint in joints:
        angles[f"left-{joint}"] = _angleFrom3Points(
            (landmarks[f"left-{joints[joint][0]}"].x,   landmarks[f"left-{joints[joint][0]}"].y ),
            (landmarks[f"left-{joint}"].x,           landmarks[f"left-{joint}"].y ),
            (landmarks[f"left-{joints[joint][1]}"].x,   landmarks[f"left-{joints[joint][1]}"].y ),
            )
        angles[f"right-{joint}"] = _angleFrom3Points(
            (landmarks[f"right-{joints[joint][0]}"].x,   landmarks[f"right-{joints[joint][0]}"].y ),
            (landmarks[f"right-{joint}"].x,           landmarks[f"right-{joint}"].y ),
            (landmarks[f"right-{joints[joint][1]}"].x,   landmarks[f"right-{joints[joint][1]}"].y ),
            )
    print(str(angles), file=sys.stderr)


def _angleFrom3Points(p1:tuple, p2:tuple, p3:tuple) -> float:
    angle = 0.0
    return angle

def _scoreFromAngles(angle:float, target:float, weight:float) -> float:
    score = 0.0
    return score
    
def _colourFromScore(score:float, bestColour:tuple, worstColour:tuple) -> tuple:
    finalColour = (255,255,255)
    return finalColour


main()