import sys, time
import mediapipe as mp
import cv2 as cv

from .utils import SqliteController as db
from .utils import formatResult, drawLandmarks

class Landmarker:
    def __init__(self, model_path:str, options={"width": 640, "height":480}):
        # Carry Forward Variables - To avoid crashing
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
        self.time_in_pause = 0.0
        self.time_in_step = 0.0
        self.running = False
        self.isSessionSet = False
        self.flagExit = False
        self.isRecording = False
        self.query = ""
        self.maxPoseSteps = 10
        self.current_poseStep = 0
        self.poseList = []
        self.current_poseDuration = 1000
        self.current_poseTargets = {
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
        self._currentFrame  = None
        self.current_Frame   = None
        # MediaPipe Pose Landmarker Options
        self.BaseOptions            = mp.tasks.BaseOptions
        self.PoseLandmarker         = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions  = mp.tasks.vision.PoseLandmarkerOptions
        self.VisionRunningMode      = mp.tasks.vision.RunningMode
        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=self._on_detect
            )

#region ----- Public Methods -----

    ## Records a new session in the database and updates the pose list
    def setSessionData(self, userId=0, sequenceId=0, deviceId=0, noCV=False, imshow=False):
        self.userId     = userId
        self.sequenceId = sequenceId
        self.deviceId   = deviceId
        self.noCV       = noCV
        self.imshow     = imshow

        # Set Session Data in Database and Close it for the video thread to access.
        self.db = db()
        self.db.runInsert(f""" 
            INSERT INTO session (userId, sequenceId) VALUES ({self.userId}, {self.sequenceId});
        """)
        self.poseList = self.db.runSelectAll(f"SELECT * FROM pose WHERE sequenceId={self.sequenceId};")
        _sessionId_res = self.db.runSelectOne(f"SELECT MAX(sessionId) FROM session;")
        self.db.closeConnection()
        self.db = None

        # Validate Data.
        if len(self.poseList) == 0  : raise Exception("Unsuccessful poseList Query @ setSessionData")
        if len(_sessionId_res) == 0 : raise Exception("Unsuccessful sessionId Query @ setSessionData")
        self.sessionId = _sessionId_res[0]
        self.maxPoseSteps = len(self.poseList)

        self.isSessionSet = True
        self._setNextPose()


    ## Gets the latest frame data in the queue
    def getFrame(self) -> bytes:
        try: return self.current_Frame
        except: return None

    def startRec(self):
        self.isRecording = True

    def stopRec(self):
        self.isRecording = False
        
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
        self.db.runInsert(f"INSERT INTO session (userId, sequenceId) VALUES ({self.userId}, {self.sequenceId});")
        
        # Start video capture
        self.feed = cv.VideoCapture(self.deviceId)
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
            
            landmarker.detect_async(mp_image, t)
            t += 1
            
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
            if not self.isRecording: 
                self.time_in_pause = time.time()
                continue

            if self.time_in_pause > 0.0:
                self.start_time += (self.time_in_pause - self.start_time)
                self.time_in_pause = 0.0
            
            self.stop_time = time.time()
            if (self.stop_time-self.start_time) >= 2:
                self._recScores()
                self._stop_or_next()
                self.start_time = time.time()

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
        except Exception as e:
            print(e, file=sys.stderr)
            nextLandmarks = self._last_landmarks
        
        # Use cv2 to draw the landmarks into the frame taken from the queue
        cvimg = cv.cvtColor(output_image.numpy_view(), cv.COLOR_BGR2RGB)

        if not self.noCV or self.isRecording:
            try:
                scores, cvimg = drawLandmarks(
                    cvimg, 
                    (self.frameWidth, self.frameHeight),
                    nextLandmarks, 
                    self.current_poseTargets
                    )
            except Exception as e:
                print("Error Drawing Landmarks:", e, file=sys.stderr)

        # Encode the frame data to jpeg numpy array, then convert to bytes, then put final frame in queue
        try:
            _, data = cv.imencode('.jpeg', cvimg)
            data_bytes = data.tobytes()
            self.current_Frame = data_bytes
            self._currentFrame = cvimg
        except Exception as e:
            print(e, file=sys.stderr)

        # Run every 300ms
        if timestamp_ms % 20 != 0: return
        if not self.isSessionSet: return
        scoreQuery = formatResult(self.sessionId, scores, self.current_poseStep)
        if scoreQuery != "": self.query = scoreQuery

    # Get the next pose in the pose list and set the state variables as needed
    def _setNextPose(self):
        nextPose = self.poseList.pop(0)
        self.time_in_step = 0.0
        self.current_poseStep += 1
        self.current_poseId = nextPose[0]
        self.current_poseDuration = nextPose[12]
        self.current_poseTargets = {
            "left-elbow": nextPose[4], 
            "right-elbow": nextPose[5], 
            "left-shoulder": nextPose[8], 
            "right-shoulder": nextPose[9], 
            "left-hip": nextPose[10], 
            "right-hip": nextPose[11], 
            "left-knee": nextPose[6], 
            "right-knee": nextPose[7]
        }
        print(f"Pose Step is now: {self.current_poseStep}", file=sys.stderr, end='\r\n')

    # Insert scores into database every x seconds.
    def _recScores(self):
        if len(self.query) != 0:
            self.db.runInsert(self.query)
            self.query = ""

    # Set next pose data / stop recording after the pose duration has elapsed
    def _stop_or_next(self):
        self.time_in_step += (self.stop_time-self.start_time)
        if self.time_in_step > self.current_poseDuration: 
            if self.current_poseStep < self.maxPoseSteps:
                self._setNextPose()
            else:
                self.isRecording = False

#endregion