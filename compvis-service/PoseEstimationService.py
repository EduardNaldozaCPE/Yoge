import mediapipe as mp
import cv2 as cv
from ScoreQueue import ScoreQueue

import numpy as np
import queue
import threading

# USAGE:
#   # 1. import modules
#     import PoseEstimationService
#     import threading
# 
#   # 2. Instantiate the service
#     service = PoseEstimationService()
#
#   # 3. Set the session data at top level
#   # (This creates a new record in yoge.session)
#     service.setSessionData()
#   
#   # 4. Create a separate thread for runVideo loop
#     video_thread = threading.Thread(target=poseEstimationService.runVideo)
#     video_thread.start()
# 
#   # 5. Get the last frame data using PoseEstimationService.getFrameData()
#     frame_data = service.getFrameData()

class PoseEstimationService:
    def __init__(self):
        # Initialise Class States
        # NOTE -- Leave the business logic @ top level. So leave the userId and sessionId as arguments 
        self.userId = None
        self.sequenceId = None
        self.sessionId = None
        self.scoreQueue:ScoreQueue = None
        self.frame_queue = queue.Queue(10)
        self.running = False

        # Initialise MediaPipe Pose Landmarker
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        self.feed = None

        def print_result(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
            # Record result every 30ms
            if timestamp_ms % 30 != 0: return
            with open("./tests/result-dump.txt", "a") as file:
                file.write('pose landmarker result @ {}ms : {}\n'.format(timestamp_ms, result))

            if self.scoreQueue is not None:
                self.scoreQueue.addScore(result)
        
        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path="./cv/pose_landmarker_lite.task"),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=print_result)

        print("PoseEstimationService Object Created")
        
    # Creates a new session and starts recording score data to yoge.score
    def setSessionData(self, userId=0, sequenceId=0, sessionId=0):
        self.userId = userId
        self.sequenceId = sequenceId
        self.sessionId = sessionId

        self.scoreQueue = ScoreQueue(self.userId, self.sequenceId, self.sessionId)
        scoring_thread = threading.Thread(target=self.scoreQueue.processScores)
        scoring_thread.start()

    # Gets the latest frame data in the queue
    def getFrameData(self) -> bytes:
        # print("[Method Called] getFrameData()")
        return self.frame_queue.get()


    # Starts video feed and stores frame data in the queue to be sent via websocket
    # NOTE -- Run in a separate thread and stop by using PoseEstimationService.stopVideo()
    def runVideo(self):        
        # print('\n[Method Called] runVideo()')
        self.feed = cv.VideoCapture(0)
        self.running = True
        with self.PoseLandmarker.create_from_options(self.options) as landmarker:
            t = 0
            while True:
                if not self.running:
                    break

                success, frame = self.feed.read()
                frame = cv.resize(frame, (640, 480))

                if not success:
                    print("There was a problem reading the video feed.")
                    break
            
                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                if not mp_image:
                    print("could not read image") 
                    continue
                
                landmarker.detect_async(mp_image, t)
                t += 1


                # Encode the frame data to jpeg, then convert to numpy array, then convert to bytes
                _, data = cv.imencode('.jpg', frame)
                data_np = np.array(data)
                data_bytes = data_np.tobytes()
                self.frame_queue.put(data_bytes)

                # # [FOR TESTING]
                # cv.imshow('img', frame)
                # if cv.waitKey(1) & 0xFF == 27:
                #     print('Exit key pressed. Exiting...')
                #     cv.destroyAllWindows()
                #     self.feed.release()
                #     break

            cv.destroyAllWindows()
            self.feed.release()


    # Stops the video feed loop in runVideo() and stops scoreQueue from recording score data.
    def stopVideo(self):
        # print("[Method Called] stopVideo()")
        self.running = False
        self.scoreQueue.stopProcessing()

if __name__ == "__main__":
    p = PoseEstimationService()
    p.runVideo()