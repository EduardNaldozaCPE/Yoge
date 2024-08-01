class LandmarkerOptions:
    """ Use for setting width, height, and other options to use on the Landmarker Module"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deviceId = 0
        self.imshow = False
    
    def setDeviceId(self, deviceId:int):
        self.deviceId = deviceId
        return self
    
    def setImshow(self, imshow:bool):
        self.imshow = imshow
        return self