from enum import Enum
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

class Joint(Enum):
    leftShoulder    = "leftShoulder"
    rightShoulder   = "rightShoulder"
    leftElbow       = "leftElbow"
    rightElbow      = "rightElbow"
    leftHip         = "leftHip"
    rightHip        = "rightHip"
    leftKnee        = "leftKnee"
    rightKnee       = "rightKnee"
    leftWrist       = "leftWrist"
    rightWrist      = "rightWrist"
    leftAnkle       = "leftAnkle"
    rightAnkle      = "rightAnkle"

class JointLandmark:
    def __init__(self):
        self.__joints = {}
        self.__keys = []
        
    def set(self, joint:Joint, landmark: NormalizedLandmark):
        self.__joints[joint] = landmark
        self.__keys.append(joint)

    def get(self,joint:Joint):
        j = self.__joints[joint]
        if j: return self.__joints[joint]
        else: raise IndexError("Joint does not exist:", joint)

    def getKeys(self):
        return self.__keys


class JointFloat:
    """ Joint-to-Float relationship """
    def __init__(self, name):
        self.name = name
        self.__joints = {}
        self.__keys = []
        
    def set(self, joint:Joint, target: float):
        self.__joints[joint] = target
        self.__keys.append(joint)

    def get(self,joint:Joint):
        j = self.__joints[joint]
        if type(j) is float or type(j) is int: return self.__joints[joint]
        else: raise IndexError("Joint does not exist", joint)
        
    def getKeys(self):
        return self.__keys