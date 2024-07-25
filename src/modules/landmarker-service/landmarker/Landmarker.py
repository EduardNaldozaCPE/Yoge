import queue, sys
import mediapipe as mp
import cv2 as cv
import time

from .utils import SqliteController as db
from .utils import formatResult, drawLandmarks

class Landmarker:
    def __init__(self, model_path:str, options={"width": 640, "height":480}):
        # Carry Forward Variables - To avoid crashing
        self._last_mp_image = None
        self._last_landmarks = {}

        # Configuration
        self.userId = None
        self.sequenceId = None
        self.sessionId = None
        self.deviceId = None
        self.noCV = False
        # Options
        self.frameWidth = options["width"]
        self.frameHeight = options["height"]
        # State
        self.stop_time = time.time()
        self.start_time = time.time()
        self.running = False
        self.isSessionSet = False
        self.flagExit = False
        self.isRecording = False
        self.queries = queue.Queue(10)
        self.maxPoseSteps = 10
        self.currentPoseStep = 0
        self.poseList = []
        self.poseDuration = 1000
        self.currentPoseTargets = {
            # Default Pose is T-Pose
            "left-elbow": 180, 
            "right-elbow": 180, 
            "left-shoulder": 90, 
            "right-shoulder": 270, 
            "left-hip": 180, 
            "right-hip": 180, 
            "left-knee": 180, 
            "right-knee": 180
        }   
        # Queues
        self._currentFrame = None
        self.currentFrame = None
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

#region ----- Public Methods -----

    ## Records a new session in the database and updates the pose list
    def setSessionData(self, userId=0, sequenceId=0, sessionId=0, deviceId=0, noCV=False, imshow=False):
        self.userId = userId
        self.sequenceId = sequenceId
        self.sessionId = sessionId
        self.deviceId = deviceId
        self.noCV = noCV
        self.imshow = imshow
        self.isSessionSet = True

        self.db = db()
        self.poseList = self.db.runSelectAll(f"SELECT * FROM pose WHERE sequenceId={self.sequenceId};")
        self.db.closeConnection()
        self.db = None
        if self.poseList is None: raise Exception("Unsuccessful Query @ setSessionData")
        self.maxPoseSteps = len(self.poseList)
        self._setNextPose()


    ## Gets the latest frame data in the queue
    def getFrame(self) -> bytes:
        try: return self.currentFrame
        except: return None

        
    ## Stops the video feed loop in runVideo().
    def stopVideo(self):
        self.running = False


    ## Starts video feed and stores frame data in the queue - Run in a separate thread and stop by using Landmarker.stopVideo()
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
        self.feed = cv.VideoCapture(self.deviceId)
        self.isRecording = True
        self.running = True
        
        # Read the current frame in the live video, detect asynchronously
        landmarker = self.PoseLandmarker.create_from_options(self.options)
        t = 0
        while self.running:
            success, frame = self.feed.read()
            if not success:
                self.stopVideo()
                break

            frame = cv.resize(frame, (self.frameWidth, self.frameHeight))
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            if not mp_image:
                mp_image = self._last_mp_image
                print("could not read image", file=sys.stderr) 
            
            landmarker.detect_async(mp_image, t)
            t += 1
            self._last_mp_image = mp_image
            
            # DEBUG (-imshow)
            if self.imshow:
                try:
                    cv.imshow("debug_imshow", self._currentFrame)
                    if cv.waitKey(1) & 0xFF == ord('q'):
                        self.feed.release()
                        cv.destroyAllWindows()
                except Exception as e:
                    print(e, file=sys.stderr)

            # Record scores every 2 seconds.
            if not self.isRecording: continue
            if (t%20 == 0) and not self.queries.empty():
                self.db.runInsert(self.queries.get())

            self.stop_time = time.time()
            if (self.stop_time-self.start_time) >= 2:
                print(f"\n{self.poseDuration}", file=sys.stderr)
                print("\nTIME ELAPSED SINCE LAST LOOP:",(self.stop_time-self.start_time), file=sys.stderr)
                self.start_time = time.time()

                if self.currentPoseStep < self.maxPoseSteps:
                    self._setNextPose()
                else:
                    self.isRecording = False

        self.feed.release()
        landmarker.close()
        self.flagExit = True
#endregion

#region   ----- Private Methods -----
 
    ## Handle Async image detect
    def _on_detect(self, result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        try:
            nextLandmarks = {
                "left-shoulder"  : result.pose_landmarks[0][11],
                "right-shoulder" : result.pose_landmarks[0][12],
                "left-elbow"     : result.pose_landmarks[0][13],
                "right-elbow"    : result.pose_landmarks[0][14],
                "left-hip"       : result.pose_landmarks[0][23],
                "right-hip"      : result.pose_landmarks[0][24],
                "left-knee"      : result.pose_landmarks[0][25],
                "right-knee"     : result.pose_landmarks[0][26],
                # Only for calculations
                "left-wrist"    : result.pose_landmarks[0][15],
                "right-wrist"   : result.pose_landmarks[0][16],
                "left-ankle"    : result.pose_landmarks[0][27],
                "right-ankle"   : result.pose_landmarks[0][28]
            }
            self._last_landmarks = nextLandmarks
        except IndexError as e: 
            nextLandmarks = self._last_landmarks
        
        # Use cv2 to draw the landmarks into the frame taken from the queue
        try:
            cvimg = cv.cvtColor(output_image.numpy_view(), cv.COLOR_BGR2RGB)
        except Exception as e: print(e, file=sys.stderr)

        if not self.noCV or self.isRecording:
            try:
                scores, cvimg = drawLandmarks(
                    cvimg, 
                    (self.frameWidth, self.frameHeight),
                    nextLandmarks, 
                    self.currentPoseTargets
                    )
            except Exception as e:
                print("Error Drawing Landmarks:", e, file=sys.stderr)

        # Encode the frame data to jpeg numpy array, then convert to bytes, then put final frame in queue
        _, data = cv.imencode('.jpeg', cvimg)
        data_bytes = data.tobytes()
        self.currentFrame = data_bytes
        self._currentFrame = cvimg

        # Run every 300ms
        if timestamp_ms % 20 != 0 and timestamp_ms > 0: return
        if not self.isSessionSet: return

        scoreQuery = formatResult(self.sessionId, scores, timestamp_ms)
        if scoreQuery != "":
            self.queries.put(scoreQuery)


    def _setNextPose(self):
        nextPose = self.poseList.pop(0)
        self.currentPoseStep += 1
        self.currentPoseId = nextPose[0]
        self.poseDuration = nextPose[12]
        self.currentPoseTargets = {
            "left-elbow": nextPose[4], 
            "right-elbow": nextPose[5], 
            "left-shoulder": nextPose[8], 
            "right-shoulder": nextPose[9], 
            "left-hip": nextPose[10], 
            "right-hip": nextPose[11], 
            "left-knee": nextPose[6], 
            "right-knee": nextPose[7]
        }
        print(f"\nNext Pose Step: {self.currentPoseStep}", file=sys.stderr)

#endregion