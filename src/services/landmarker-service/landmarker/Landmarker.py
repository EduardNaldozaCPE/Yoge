import sys, time
import mediapipe as mp
import cv2 as cv

from .Joints import *
from .utils import *
from session import Session
from sqlite_controller import SqliteController as db
from .LandmarkerOptions import LandmarkerOptions

class Landmarker:
    """Captures the image data, draws Landmarks via MediaPipe, and encodes image to bytes. 

    Uses OpenCV to capture video, MediaPipe Pose Landmarker Solution to asynchronously detect pose landmarks from the video frame
    Draws on to the detected frame via OpenCV, and stores the latest frame in bytes that can be accessed using `getFrame()`.
    """
    def __init__(self, model_path:str, session:Session, options:LandmarkerOptions):
        # Carry Forward Variables - To avoid crashing
        self.__landmarks = JointLandmark()

        # Options
        self.session = session
        self.landmarker_options = options

        # Timing
        self.stop_time  = time.time()
        self.start_time = time.time()
        self.time_in_pause = 0.0
        self.time_in_step  = 0.0

        # State
        self._current_frame_cv = None
        self._current_frame  = None
        self.running        = False
        self.flagExit       = False
        self.isRecording    = False
        self.query = ""
        self.maxPoseSteps   = 10
        self.current_poseStep = 0
        self.poseList = []
        self.current_poseDuration = 1000
        self.current_poseTargets = JointFloat('targets')
        self.current_poseTargets.set(Joint.leftElbow,  180.0)
        self.current_poseTargets.set(Joint.rightElbow,  180.0)
        self.current_poseTargets.set(Joint.leftShoulder,  90.0)
        self.current_poseTargets.set(Joint.rightShoulder,  270.0)
        self.current_poseTargets.set(Joint.leftHip,  180.0)
        self.current_poseTargets.set(Joint.rightHip,  180.0)
        self.current_poseTargets.set(Joint.leftKnee,  180.0)
        self.current_poseTargets.set(Joint.rightKnee,  180.0)

        # Result
        self.__result: mp.tasks.vision.PoseLandmarkerResult
        self.__output_image: mp.Image
        self.__timestamp_ms: int
        self.__gotImage:bool = False

        
        # MediaPipe Pose Landmarker Options
        self.BaseOptions            = mp.tasks.BaseOptions
        self.PoseLandmarker         = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions  = mp.tasks.vision.PoseLandmarkerOptions
        self.VisionRunningMode      = mp.tasks.vision.RunningMode
        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=self.__on_detect
            )
        
        # Validate session
        self.isSessionSet = self.session.validateSession()
        if (not self.isSessionSet): raise Exception("Error in validating the Session")
        self.db = db()
        self.poseList = self.db.runSelectAll(f"SELECT * FROM pose WHERE sequenceId={self.session.sequenceId};")
        self.db.closeConnection()
        self.db = None

        # Validate Data.
        self.maxPoseSteps = len(self.poseList)
        self.isSessionSet = True
        self.__setNextPose()


    def getFrame(self) -> bytes:
        """ Gets the latest frame data in the queue. """
        try: return self._current_frame
        except: return None


    def startRec(self):
        """ Runs the score-related functions. """
        self.isRecording = True


    def stopRec(self):
        """ Skips the score-related functions. """
        self.isRecording = False
        

    def stopVideo(self):
        """ Stops the video feed loop in runVideo()."""
        self.running = False


    def runVideo(self):
        """ Starts video feed and stores frame data in the queue - Run in a separate thread and stop by using Landmarker.stopVideo() """
        if not self.isSessionSet:
            print("Session Data has not been set. Use setSessionData() before calling runVideo()", file=sys.stderr)
            return
        
        # Create a new row in the session table
        self.db = db()
        
        # Start video capture
        self.feed = cv.VideoCapture(self.landmarker_options.deviceId)
        self.running = True
        
        # Read the current frame in the live video, detect asynchronously
        landmarker = self.PoseLandmarker.create_from_options(self.options)
        t = 0
        while self.running:
            success, frame = self.feed.read()
            if not success:
                self.stopVideo()
                break

            frame = cv.resize(frame, (self.landmarker_options.width, self.landmarker_options.height))
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            
            landmarker.detect_async(mp_image, t)
            t += 1

            if (self.__gotImage): 
                self.__score_and_draw()
            
            # DEBUG (-imshow)
            if self.landmarker_options.imshow:
                try:
                    cv.imshow("debug_imshow", self._current_frame_cv)
                    if cv.waitKey(1) & 0xFF == ord('q'):
                        self.feed.release()
                        cv.destroyAllWindows()
                except Exception as e:
                    print("Error @ imshow: ", e, file=sys.stderr)

            # Record scores every 2 seconds & account for paused time. 
            if not self.isRecording: 
                self.time_in_pause = time.time()
                continue

            if self.time_in_pause > 0.0:
                self.start_time += (self.time_in_pause - self.start_time)
                self.time_in_pause = 0.0
            
            self.stop_time = time.time()
            if (self.stop_time-self.start_time) >= 2:
                self.__recScores()
                self.__stop_or_next()
                self.start_time = time.time()

        self.feed.release()
        landmarker.close()
        self.flagExit = True


    def __score_and_draw(self):
        try:
            self.__landmarks.set(Joint.leftShoulder , self.__result.pose_landmarks[0][11])
            self.__landmarks.set(Joint.rightShoulder, self.__result.pose_landmarks[0][12])
            self.__landmarks.set(Joint.leftElbow    , self.__result.pose_landmarks[0][13])
            self.__landmarks.set(Joint.rightElbow   , self.__result.pose_landmarks[0][14])
            self.__landmarks.set(Joint.leftHip      , self.__result.pose_landmarks[0][23])
            self.__landmarks.set(Joint.rightHip     , self.__result.pose_landmarks[0][24])
            self.__landmarks.set(Joint.leftKnee     , self.__result.pose_landmarks[0][25])
            self.__landmarks.set(Joint.rightKnee    , self.__result.pose_landmarks[0][26])
            self.__landmarks.set(Joint.leftWrist , self.__result.pose_landmarks[0][15])
            self.__landmarks.set(Joint.rightWrist, self.__result.pose_landmarks[0][16])
            self.__landmarks.set(Joint.leftAnkle , self.__result.pose_landmarks[0][27])
            self.__landmarks.set(Joint.rightAnkle, self.__result.pose_landmarks[0][28])
            isResultComplete = True
        except IndexError as e:
            isResultComplete = False
        except Exception as e:
            print("Error @ __score_and_draw():", e, file=sys.stderr)
            return
        
        # Use cv2 to draw the landmarks into the frame taken from the queue
        cvimg = cv.cvtColor(self.__output_image.numpy_view(), cv.COLOR_BGR2RGB)
        scores = calculateScores(self.__landmarks, self.current_poseTargets)
        cvimg = drawLandmarks(
            cvimg, self.landmarker_options.width, self.landmarker_options.height,
            self.__landmarks, scores
            )

        debug_isRecStr = "RECORDING: TRUE" if self.isRecording else "RECORDING: FALSE"  
        cvimg = cv.putText(
            cvimg, debug_isRecStr,
            ( 10, 140 ), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8,
            ( 150, 50, 0 ), 1, cv.LINE_AA, False)
        
        debug_isRecStr = "RESULT: COMPLETE" if isResultComplete else "RESULT: INCOMPLETE"  
        cvimg = cv.putText(
            cvimg, debug_isRecStr,
            ( 10, 120 ), cv.FONT_HERSHEY_COMPLEX_SMALL, 0.8,
            ( 150, 50, 0 ), 1, cv.LINE_AA, False)
        
        # Encode the frame data to jpeg numpy array, then convert to bytes, then put final frame in queue
        try:
            _, data = cv.imencode('.jpeg', cvimg)
            data_bytes = data.tobytes()
            self._current_frame = data_bytes
            self._current_frame_cv = cvimg
        except Exception as e:
            print("Error Encoding cvimg @ __score_and_draw() "+e, file=sys.stderr)

        # Run every 300ms
        if self.isRecording:
            if self.__timestamp_ms % 20 != 0: return
            if not self.isSessionSet: return
            self.query = formatResult(self.session.sessionId, scores, self.current_poseStep)

        self.__gotImage = False
 

    def __on_detect(self, result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        """Private Method - Handle Async image detect """
        self.__result = result
        self.__output_image = output_image
        self.__timestamp_ms = timestamp_ms
        self.__gotImage = True


    def __setNextPose(self):
        """ Private Method - Get the next pose in the pose list and set the state variables as needed """
        nextPose = self.poseList.pop(0)
        self.time_in_step = 0.0
        self.current_poseStep += 1
        self.current_poseId = nextPose[0]
        self.current_poseDuration = nextPose[12]
        self.current_poseTargets.set(Joint.leftElbow, nextPose[4])
        self.current_poseTargets.set(Joint.rightElbow, nextPose[5])
        self.current_poseTargets.set(Joint.leftShoulder, nextPose[8])
        self.current_poseTargets.set(Joint.rightShoulder, nextPose[9])
        self.current_poseTargets.set(Joint.leftHip, nextPose[10])
        self.current_poseTargets.set(Joint.rightHip, nextPose[11])
        self.current_poseTargets.set(Joint.leftKnee, nextPose[6])
        self.current_poseTargets.set(Joint.rightKnee, nextPose[7])

        print(f"NPOSE={self.current_poseStep}", file=sys.stderr, end='\r\n')

    def __recScores(self):
        """ Private Method - Insert scores into database every x seconds."""
        if len(self.query) > 0:
            self.db.runInsert(self.query)
            self.query = ""

    def __stop_or_next(self):
        """Private Method - Set next pose data / stop recording after the pose duration has elapsed """
        self.time_in_step += (self.stop_time-self.start_time)
        if self.time_in_step > self.current_poseDuration:
            if self.current_poseStep < self.maxPoseSteps:
                self.__setNextPose()
            else:
                self.isRecording = False