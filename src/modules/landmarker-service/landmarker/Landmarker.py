import queue, sys
import mediapipe as mp
import cv2 as cv
from threading import Thread

from .utils.score_queue import ScoreQueue

class Landmarker:
    def __init__(self, model_path:str, options={"width": 640, "height":480}):
        # Options
        self.frameWidth = options["width"]
        self.frameheight = options["height"]
        # State
        self.userId = None
        self.sequenceId = None
        self.sessionId = None
        self.running = False
        # Queues
        self.scoreQueue : ScoreQueue = None
        self.frame_queue = queue.Queue(10)
        self.landmark_queue = queue.Queue(10)
        # MediaPipe Pose Landmarker Options
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        # Threads
        self.scoring_thread:Thread = None

        # Record result every 30ms
        def record_score(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
            pass
            # if timestamp_ms % 20 != 0: return
            # if self.scoreQueue is not None:
            #     self.scoreQueue.addScore(result, timestamp_ms)
        
        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=record_score)
        
    

    # Creates a new session and starts recording score data to yoge.score
    def setSessionData(self, userId=0, sequenceId=0, sessionId=0):
        self.userId = userId
        self.sequenceId = sequenceId
        self.sessionId = sessionId

        self.scoreQueue = ScoreQueue(self.userId, self.sequenceId, self.sessionId)
        # self.scoring_thread = Thread(target=self.scoreQueue.recordScores, daemon=True)
        # self.scoring_thread.start()


    # Gets the latest frame data in the queue
    def getFrame(self) -> bytes:
        try: return self.frame_queue.get()
        except: return None


    # Starts video feed and stores frame data in the queue
    # NOTE -- Run in a separate thread and stop by using Landmarker.stopVideo()
    def runVideo(self):
        if self.scoreQueue is None:
            print("Session Data has not been set. Use setSessionData() before calling runVideo()", file=sys.stderr)
            return
        
        try:
            self.feed = cv.VideoCapture(0)
            self.running = True
        except:
            print("Error running cv2.VideoCapture(). Stopping...", file=sys.stderr)
            return
        
        with self.PoseLandmarker.create_from_options(self.options) as landmarker:
            t = 0
            while True:
                if not self.running:
                    break

                success, frame = self.feed.read()
                try:
                    frame = cv.resize(frame, (self.frameWidth, self.frameheight))
                except:
                    print(f"Error running cv2.resize(). Stopping...", file=sys.stderr)
                    self.stopVideo()
                    break

                if not success:
                    print("There was a problem reading the video feed.", file=sys.stderr)
                    self.stopVideo()
                    break
            
                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                if not mp_image:
                    print("could not read image", file=sys.stderr) 
                    continue
                
                landmarker.detect_async(mp_image, t)
                t += 1

                # TODO -- Use cv2 to draw the landmarks into the frame taken from the queue
                # nextLandmarks = landmark_queue.get()
                # markedFrame = drawLandmarks(mp_image, nextLandmarks)

                # Encode the frame data to jpeg, then convert to numpy array, then convert to bytes
                _, data = cv.imencode('.jpeg', frame)
                data_bytes = data.tobytes()
                self.frame_queue.put(data_bytes)

            self.feed.release()
            cv.destroyAllWindows()


    # Stops the video feed loop in runVideo() and stops scoreQueue from recording score data.
    def stopVideo(self):
        self.running = False
        # self.scoring_thread.join()
        self.scoreQueue.stopProcessing()

if __name__ == "__main__":
    p = Landmarker()
    p.runVideo()