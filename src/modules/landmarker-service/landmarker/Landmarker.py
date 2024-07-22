import queue, sys
import mediapipe as mp
import cv2 as cv

from .utils import SqliteController as db
from .utils import formatResult, drawLandmarks

class Landmarker:
    def __init__(self, model_path:str, options={"width": 640, "height":480}):
        # Options
        self.frameWidth = options["width"]
        self.frameHeight = options["height"]
        # State
        self.userId = None
        self.sequenceId = None
        self.sessionId = None
        self.running = False
        self.isSessionSet = False
        self.queries = queue.Queue(10)
        # Queues
        self.frame_queue = queue.Queue(10)
        self.lastLandmarks:mp.tasks.vision.PoseLandmarkerResult
        # MediaPipe Pose Landmarker Options
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        
        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=self._on_detect
            )

        
    def __del__(self):
        pass


    # Handle Async image detect
    def _on_detect(self, result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):

        # Use cv2 to draw the landmarks into the frame taken from the queue
        cvimg = cv.cvtColor(output_image.numpy_view(), cv.COLOR_BGR2RGB)
        try:
            nextLandmarks = {
                "leftShoulder"  : result.pose_landmarks[0][11],
                "rightShoulder" : result.pose_landmarks[0][12],
                "leftElbow"     : result.pose_landmarks[0][13],
                "rightElbow"    : result.pose_landmarks[0][14],
                "leftHip"       : result.pose_landmarks[0][23],
                "rightHip"      : result.pose_landmarks[0][24],
                "leftKnee"      : result.pose_landmarks[0][25],
                "rightKnee"     : result.pose_landmarks[0][26],
            }
            cvimg = drawLandmarks(cvimg, (self.frameWidth, self.frameHeight), nextLandmarks)
        except AttributeError as e:
            print("Error Drawing Landmarks:", e, file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)

        # Encode the frame data to jpeg numpy array, then convert to bytes, then put final frame in queue
        _, data = cv.imencode('.jpeg', cvimg)
        data_bytes = data.tobytes()
        self.frame_queue.put(data_bytes)

        # Run every 300ms
        if timestamp_ms % 20 != 0 and timestamp_ms != 0: return
        if not self.isSessionSet: return

        scoreQuery = formatResult(self.sessionId, result, timestamp_ms)
        if scoreQuery != "": 
            self.queries.put(scoreQuery)


    # Records a new session in the database
    def setSessionData(self, userId=0, sequenceId=0, sessionId=0):
        self.userId = userId
        self.sequenceId = sequenceId
        self.sessionId = sessionId
        self.isSessionSet = True


    # Gets the latest frame data in the queue
    def getFrame(self) -> bytes:
        try: return self.frame_queue.get()
        except: return None


    # Starts video feed and stores frame data in the queue
    # NOTE -- Run in a separate thread and stop by using Landmarker.stopVideo()
    def runVideo(self):
        if not self.isSessionSet:
            print("Session Data has not been set. Use setSessionData() before calling runVideo()", file=sys.stderr)
            return
        
        # Create a new row in the session table
        self.db = db()
        self.db.runInsert(f""" 
            INSERT INTO session (userId, sequenceId) VALUES ({self.userId}, {self.sequenceId});
        """)
        
        # Start video capture
        try:
            self.feed = cv.VideoCapture(0)
            self.running = True
        except:
            print("Error running cv2.VideoCapture(). Stopping...", file=sys.stderr)
            return
        
        # Read the current frame in the live video, detect asynchronously
        with self.PoseLandmarker.create_from_options(self.options) as landmarker:
            t = 0
            while self.running:
                success, frame = self.feed.read()
                if not success:
                    print("There was a problem reading the video feed.", file=sys.stderr)
                    self.stopVideo()
                    break

                frame = cv.resize(frame, (self.frameWidth, self.frameHeight))
                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                if not mp_image:
                    print("could not read image", file=sys.stderr) 
                    continue
                
                landmarker.detect_async(mp_image, t)
                t += 1

                # Record scores every 2 seconds
                if (t%20 == 0) and not self.queries.empty():
                    self.db.runInsert(self.queries.get())

            self.feed.release()
            cv.destroyAllWindows()


    # Stops the video feed loop in runVideo().
    def stopVideo(self):
        self.running = False

if __name__ == "__main__":
    p = Landmarker()
    p.runVideo()