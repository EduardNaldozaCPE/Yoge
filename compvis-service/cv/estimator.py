from tkinter import Image
import mediapipe as mp
import cv2

# Used to detect pose, draw over detected landmarks, and calculate landmark angles

class poseDetector():
    def __init__(self):

        self.model_path = "data\\pose_landmarker_lite.task"
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
        self.VisionRunningMode = mp.tasks.vision.RunningMode

        self.mp_image = None

        # Create a pose landmarker instance with the live stream mode:
        def print_result(result : mp.tasks.vision.PoseLandmarkerOptions, output_image: mp.Image, timestamp_ms: int):
            # print('pose landmarker result: {}'.format(result))
            pass

        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=self.model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=print_result)

        self.feed = cv2.VideoCapture(0)


    # Returns image with detected landmarks drawn and DRAW LANDMARK CONNECTIONS / LIMB LINES
    def processFrame(self):
        ret, self.img = self.feed.read()
        frame_rgb = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=self.img)
        
        with self.PoseLandmarker.create_from_options(self.options) as landmarker:
            landmarker.detect_async(self.mp_image, 10)
        
    def showFrame(self):
        cv2.imshow('img', self.img)

    # Returns the angle of a joint from 3 landmarks
    # def findAngle(self, img, p1, p2, p3, draw=True):
    #     x1, y1 = self.lmList[p1][1:]
    #     x2, y2 = self.lmList[p2][1:]
    #     x3, y3 = self.lmList[p3][1:]

    #     angle = math.degrees(math.atan2(y3-y2, x3-x2) - math.atan2(y1-y2, x1-x2))

    #     if angle < 0:
    #         angle += 360
    #     # print(angle)

    #     # if draw:
    #         # cv2.circle(img, (x1, y1), 5, (255, 0, 0), cv2.FILLED)
    #         # cv2.circle(img, (x2, y2), 5, (255, 0, 0), cv2.FILLED)
    #         # cv2.circle(img, (x3, y3), 5, (255, 0, 0), cv2.FILLED)
    #     return angle
    
    # HIGHLIGHT LIMB (TWO POINTS) WITH CORRECT ANGLES
    # def highlightLimb(self, img, p1, p2, colour=(255,150,150)):
    #     x1, y1 = self.lmList[p1][1:]
    #     x2, y2 = self.lmList[p2][1:]
    #     # print('draw line')
    #     return cv2.line(img, (x1,y1), (x2,y2), colour, 9)
        


def main():
    poser = poseDetector()

    while True:
        poser.processFrame()
        poser.showFrame()
        if cv2.waitKey(1) & 0xFF == 27:
            break

if __name__ == "__main__":
    main()
