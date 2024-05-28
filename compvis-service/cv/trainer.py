# Written by Eduard Naldoza, Bachelor of Science in Computer Engineering
# De La Salle University - Dasmariñas (2022)
# https://github.com/EduardNaldozaCPE/yogaposeestim-Thesis


import cv2
import time
from . import estimator as pm
import math
import os.path
from sqlite3 import Connection, Cursor
from pathlib import Path
import threading


def getScore(a, a2):
    # 90 degrees counter-clockwise of target angle 
    a2_90cc = a2 - 90
    # 90 degrees clockwise of target angle 
    a2_90c = a2 + 90

    # If the a2_90cc is below 0, wrap the angle and include scores for angles below 0
    if a2_90cc < 0:
        a2_90cc += 360
        # if a is within the normal range between 0 to target angle
        if 0 < a <= a2:          return int(100-((abs(a - a2)/90)*100))
        # if a is within the normal range between target angle to a2_90c
        elif a2 <= a < a2_90c:   return int(100-((abs(a - a2)/90)*100))
        # if a is within the extended range between a2_90cc to 0 to target angle
        elif a2_90cc < a < 360: return int(100-(((a2-(a-360))/90)*100))
        # if a is not within scoring range
        else:                   return 0 
            
    # If the a2_90c is above 360, wrap the angle and include scores for angles above 360 
    elif a2_90c > 360:
        a2_90c -= 360
        # if a is within the normal range between target angle to 360
        if a2 <= a < 360:        return int(100-((abs(a - a2)/90)*100))
        # if a is within the normal range between a2_90cc to target angle 
        if a2_90cc < a <= a2:    return int(100-((abs(a - a2)/90)*100))
        # if a is within the extended range between target angle to 0 to a2_90c 
        if 0 < a < a2_90c:      return int(100-((abs(a2-(a+360))/90)*100)) 
        # if a is not within scoring range
        else:                   return 0 
    
    else:
        if a2 <= a < a2_90c:     return int(100-((abs(a - a2)/90)*100))
        if a2_90cc < a <= a2:    return int(100-((abs(a - a2)/90)*100))
        else:                   return 0


# Used Pose Detection, Image Processing (Landmark Drawing), and Scoring


# Usage:
#   1.  Create Video Object
# 
#   2.  Start a video using gen() which will use get_frame()
#       2a. Using get_frame() will requires starting Sequence ID and Sequence Step arguments to start.
#       2b. Video Object's Sequence ID and Sequence Step is stored in sqlite's in-memory database.
#       2c. User scores for the session is also stored in sqlite's in-memory database.
#       2d. User scores are stored/updated every 2 seconds as long as the video feed is active. 
# 
#       NOTE:
#           ONCE get_frame() IS CALLED (via gen() outside of the Video object), THE VIDEO FEED AND CAMERA WILL STAY ACTIVE UNLESS STOPPED 
#           If gen() encounters an error or if a camera device does not exist with the corresponding camInt (self.camInt),
#           The programme will instead display an image indicating the error. 
# 
#   3.  Change the sequence step by using readMem_session and writetoMem_session to change in-memory session
# 
#   4.  Stop the running video feed using stop_video()
# 
#   5.  Stop the entire session by deleting the Video object (runs __del__() method)

class Video(object):
    def __init__(self, userId, sessionId, conn: Connection, c: Cursor):
        self.sessionId = sessionId
        self.pTime = 0                      # Time of previous frame
        self.startTime = time.time()
        self.camInt = 0
        self.video = cv2.VideoCapture(self.camInt)    # OpenCV video capture
        self.detector = pm.poseDetector()   # PoseModule Pose Detector object
        self.running = False
        self.seqId = None
        self.seqStep = None
        self.userId = userId
        self.conn = conn
        self.c = c
        self.csvFile = None
        self.JointWrongAngleTimer = [0,0,0,0,0,0]
        self.JointWrongAngleComments = ["","","","","",""]
        self.landmark_angles = [[0,0,0,0,0,0]]
        self.lock = threading.Lock()

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()
    
    def stop_video(self):
        self.video.release()
        cv2.destroyAllWindows()

    def run(self):
        self.running = True
    
    def stop(self):
        self.running = False

    def writeToMem_session(self, s: list, fn: str):
        # CREATE IN MEMORY TABLE IF IT DOES NOT ALREADY EXIST
        n_fn = fn.split('_')
        seqId = s[0]
        seqStep = s[1]
        userId = n_fn[2]
        with self.conn:
            # print("\nwriteToMem_session 1")
            try:
                self.lock.acquire()
                self.c.execute(f"""
                CREATE TABLE IF NOT EXISTS sessions (
                userId INTEGER, seqId INTEGER, seqStep INTEGER
                );
                """)
            except Exception as e:
                print("\nwriteToMem_session: Memory Table already exists")
            finally:
                self.lock.release()
            # print("\nwriteToMem_session 1")
        # INSERT / UPDATE SPECIFIED ROW
            # 1. CHECK IF THE SEQUENCE AND STEP IS ALREADY LOGGED
            try:
                self.lock.acquire()
                self.c.execute(f"""SELECT * FROM sessions WHERE userId={userId}""")
            finally:
                self.lock.release()
            # print("\nwriteToMem_session 2")
            
            # 2a. IF IT DOESN'T EXIST, CREATE A NEW ROW WITH VALUES
            if len(self.c.fetchall()) == 0:
                print(f'\nNo row for userId = {userId}\nInserting new row in sessions')
                try:
                    self.lock.acquire()
                    self.c.execute(f"""
                        INSERT INTO sessions
                        VALUES ({userId}, {seqId}, {seqStep});
                        """)
                    # print("\nwriteToMem_session 3a")
                finally:
                    self.lock.release()
                    
            # 2b. IF IT ALREADY EXISTS, UPDATE THW ROW
            else:
                print(f'Row Exists\nUpdating row in sessions for userId={userId}')
                try:
                    self.lock.acquire()
                    self.c.execute(f"""
                        UPDATE sessions
                        SET seqId={seqId}, seqStep={seqStep}
                        WHERE userId = {userId};
                        """)
                    # print("\nwriteToMem_session 3b")
                finally:
                    self.lock.release()
    
    def writeToMem(self, conn: Connection, c: Cursor, s: list, fn: str):
        n_fn = fn.split('_')
        userId = n_fn[0]
        seqId = n_fn[1]
        seqStep = n_fn[2]
        # print(f"{seqId}, {seqStep}, {s[0]}, {s[1]}, {s[2]}, {s[3]}, {s[4]}, {s[5]}")
        # CREATE IN MEMORY TABLE IF IT DOES NOT ALREADY EXIST
        # INSERT / UPDATE SPECIFIED ROW
        with conn:
            # print("\nwriteToMem 1")
            try:
                self.lock.acquire()
                c.execute(f"""CREATE TABLE IF NOT EXISTS session_user_{userId} (
                    seqId INTEGER, seqStep INTEGER, leftElbow REAL, rightElbow REAL, leftKnee REAL, rightKnee REAL, leftHip REAL, rightHip REAL
                );""")
            except Exception as e:
                # print("\nwriteToMem: Memory Table already exists")
                pass
            finally:
                self.lock.release()

            # print("\nwriteToMem 2")

            # 1. CHECK IF THE SEQUENCE AND STEP IS ALREADY LOGGED
            try:
                self.lock.acquire()
                c.execute(f"""SELECT seqId, seqStep FROM session_user_{userId} WHERE seqId = {seqId} AND seqStep = {seqStep}""")
            finally:
                self.lock.release()
            
            # print("\nwriteToMem 3")

            # 2a. IF IT DOESN'T EXIST, CREATE A NEW ROW WITH VALUES
            if len(c.fetchall()) == 0:
                # print(f'\nNo row with seqId = {seqId} AND seqStep = {seqStep}\nInserting new row in session_user_{userId}')
                try:
                    self.lock.acquire()
                    c.execute(f"""
                        INSERT INTO session_user_{userId}
                        VALUES ({seqId}, {seqStep}, {s[0]}, {s[1]}, {s[2]}, {s[3]}, {s[4]}, {s[5]});
                        """)
                # print("\nwriteToMem 5a")
                finally:
                    self.lock.release()
                    
            # 2b. IF IT ALREADY EXISTS, UPDATE THE ROW
            else:
                # print(f'Row Exists\nUpdating row in session_user_{userId}')
                try:
                    self.lock.acquire()
                    c.execute(f"""
                        UPDATE session_user_{userId}
                        SET leftElbow={s[0]}, rightElbow={s[1]}, leftKnee={s[2]}, rightKnee={s[3]}, leftHip={s[4]}, rightHip={s[5]}
                        WHERE seqId={seqId} AND seqStep={seqStep};
                        """)
                finally:
                    self.lock.release()
                # print("\nwriteToMem 5b")

    def readMem_session(self, userId: str):
        try:
            self.lock.acquire()
            with self.conn:
                self.c.execute(f"""
                SELECT seqId, seqStep
                FROM sessions
                WHERE userId={userId}
                """)
                return self.c.fetchone()
        finally:
            self.lock.release()
    
    def readScoreInMem(self, fn: str):
        n_fn = fn.split('_')
        userId = n_fn[0]
        seqId = n_fn[1]
        seqStep = n_fn[2]
        try:
            self.lock.acquire()
            with self.conn:
                self.c.execute(f"""
                SELECT leftElbow , rightElbow , leftKnee , rightKnee , leftHip , rightHip
                FROM session_user_{userId}
                WHERE seqId={seqId} AND seqStep={seqStep}
                """)
                return self.c.fetchone()
        finally:
            self.lock.release()
    # Calculate scores, write to CSV, and Return final frame as Bytes
    def get_frame(self, pose):
        # while True:
        nTime = math.floor(time.time() - self.startTime)
        if nTime < 10: self.landmark_angles = pose['landmark_angles']
        # Get Image from video capture, use findPose to detect current pose, and get list/array of landmarks
        # and Draw landmarks
        success, self.img = self.video.read()
        self.img = self.detector.findPose(self.img)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.75
        color = (255,0,255)
        thickness = 2
        # self.img = cv2.putText(self.img, str(pose['poseName']),(100,100),font,fontScale,color,thickness,cv2.LINE_AA)
        # self.img = cv2.putText(self.img, str(self.JointWrongAngleComments),(100,300),font,fontScale,(50,255,50),thickness,cv2.LINE_AA)
        # self.img = cv2.putText(self.img, str(self.JointWrongAngleTimer),(100,200),font,fontScale,(50,255,50),thickness,cv2.LINE_AA)
        # self.img = cv2.putText(self.img, str(self.landmark_angles),(100,200),font,fontScale,(50,255,50),thickness,cv2.LINE_AA)
        self.lmList = self.detector.getLandmarks(self.img)

        # Calculate angle of each important landmark, calculate score, and write scores to memory
        try:
            if len(self.lmList) != 0:
                # print(self.lmList)
                # Calculate angle of each important landmark
                # Left Elbow
                self.angle_le = self.detector.findAngle(self.img, 11, 13, 15)
                # Right Elbow
                self.angle_re = self.detector.findAngle(self.img, 12, 14, 16)
                # Left Knee
                self.angle_lk = self.detector.findAngle(self.img, 23, 25, 27)
                # Right Knee
                self.angle_rk = self.detector.findAngle(self.img, 24, 26, 28)
                # Left Hip
                self.angle_lh = self.detector.findAngle(self.img, 11, 23, 25)
                # Right Hip
                self.angle_rh = self.detector.findAngle(self.img, 12, 24, 26)

                # [TEST] SHOW ANGLE TEXT
                # self.angle_ls = self.detector.findAngle(self.img, 13, 11, 23)
                # self.angle_rs = self.detector.findAngle(self.img, 14, 12, 24)
                # angletext_le_x, angletext_le_y = self.lmList[13][1:]
                # angletext_re_x, angletext_re_y = self.lmList[14][1:]
                # angletext_ls_x, angletext_ls_y = self.lmList[11][1:]
                # angletext_rs_x, angletext_rs_y = self.lmList[12][1:]
                # angletext_lh_x, angletext_lh_y = self.lmList[23][1:]
                # angletext_rh_x, angletext_rh_y = self.lmList[24][1:]
                # angletext_lk_x, angletext_lk_y = self.lmList[25][1:]
                # angletext_rk_x, angletext_rk_y = self.lmList[26][1:]
                # textScale = 0.85

                # self.img = cv2.putText(self.img, "L Elbow:" + str(round(self.angle_le, 3)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "R Elbow:" + str(round(self.angle_re, 3)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "L Shoulder:" + str(round(self.angle_ls, 3)), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "R Shoulder:" + str(round(self.angle_rs, 3)), (10, 110), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "L Hip:" + str(round(self.angle_lh, 3)), (10, 140), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "R Hip:" + str(round(self.angle_rh, 3)), (10, 170), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "L Knee:" + str(round(self.angle_lk, 3)), (10, 200), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                # self.img = cv2.putText(self.img, "R Knee:" + str(round(self.angle_rk, 3)), (10, 230), cv2.FONT_HERSHEY_SIMPLEX, textScale, (0,255,255), 2, cv2.LINE_AA, False)
                
                # Calculate Score
                self.scores = []
                if int(pose['poseName'].split('_')[1]) == 2 and int(pose['poseName'].split('_')[1]) == 13 or int(pose['poseName'].split('_')[1]) == 2 and int(pose['poseName'].split('_')[1]) == 14:
                    self.scores.append(100)
                    self.scores.append(100)
                else:
                    self.scores.append(
                        getScore(self.angle_le, self.landmark_angles[0][0]))
                    self.scores.append(
                        getScore(self.angle_re, self.landmark_angles[0][1]))
                self.scores.append(
                    getScore(self.angle_lk, self.landmark_angles[0][2]))
                self.scores.append(
                    getScore(self.angle_rk, self.landmark_angles[0][3]))
                self.scores.append(
                    getScore(self.angle_lh, self.landmark_angles[0][4]))
                self.scores.append(
                    getScore(self.angle_rh, self.landmark_angles[0][5]))       

                
        except Exception as e:
            print("SCORE ERROR trainer.py \r", e)
            ret, jpg = cv2.imencode('.jpg', self.img)
            return jpg.tobytes()

        try:
            if len(self.lmList) != 0:
                # print("\nlmList is not 0")
                for i_score, score in enumerate(self.scores):
                    limb = []
                    if i_score == 0: limb = [11, 13, 15]
                    if i_score == 1: limb = [12, 14, 16]
                    if i_score == 2: limb = [23, 25, 27]
                    if i_score == 3: limb = [24, 26, 28]
                    if i_score == 4: limb = [11, 23, 25]
                    if i_score == 5: limb = [12, 24, 26]
                    # if score >= 0:
                    self.img = self.detector.highlightLimb(
                        self.img, 
                        limb[0], limb[1], 
                        ((255-(score/100)*255),(score/100)*255,0)
                        )
                    self.img = self.detector.highlightLimb(
                        self.img, 
                        limb[1], 
                        limb[2],
                        ((255-(score/100)*255),(score/100)*255,0)
                        )
                # Write Scores to in-memory db
                # print("\n1sec Run")
                # print("\n1sec Running 1:",nTime,self.pTime)
                if nTime - self.pTime >= 1:
                    self.pTime = nTime
                    # print('le:', self.angle_le)
                    # print('re:', self.angle_re)
                    # print('le:', self.angle_le)
                    # print('le:', self.angle_le)
                    # print('le:', self.angle_le)
                    # print('le:', self.angle_le)
                    # print(self.scores)

                    # Time the limb when angle is incorrect and generate comment
                    for i_score, score in enumerate(self.scores):
                        if score <= 50:
                            self.JointWrongAngleTimer[i_score] += 1
                        else:
                            if score != 0: self.JointWrongAngleTimer[i_score] = 0
                            
                    # print("\n1sec Running 2")

                    for i_jointSecs, jointSecs in enumerate(self.JointWrongAngleTimer):
                        joints = [
                            "Left Elbow",
                            "Right Elbow",
                            "Left Knee",
                            "Right Knee",
                            "Left Hip",
                            "Right Hip"
                        ]
                        if 4 == jointSecs: self.JointWrongAngleComments[i_jointSecs] = "Adjust your {}".format(joints[i_jointSecs])
                        elif jointSecs > 4: 
                            self.JointWrongAngleTimer[i_jointSecs] = 0
                            self.JointWrongAngleComments[i_jointSecs] = ""
                        else: self.JointWrongAngleComments[i_jointSecs] = ""
                    
                    # print("\n1sec Running 3")
                        
                    # print('\nRUNNING WRITE TO MEM')
                    self.writeToMem(self.conn, self.c, self.scores, pose['poseName'])
                    # print('\nWRITE TO MEM RAN')
                    
                    # print("\n1sec Ran")

            # self.img = cv2.putText(self.img, str(self.scores),(100,200),font,fontScale,(50,255,50),thickness,cv2.LINE_AA)
            # Return final image as Byte string
            ret, jpg = cv2.imencode('.jpg', self.img)
            return jpg.tobytes()
        except Exception as e:
            print("LIMB HIGHLIGHT ERROR trainer.py \r", e)
            ret, jpg = cv2.imencode('.jpg', self.img)
            return jpg.tobytes()

    def set_camera(self, camInt: int):
        self.video = cv2.VideoCapture(camInt)

    def get_frame_no_pose(self):
        while True:
            try:
                if self.video is None or not self.video.isOpened():
                    return self.show_PoliteCat()
                else:
                    success, self.img = self.video.read()
                    ret, jpg = cv2.imencode('.jpg', self.img)
                    return jpg.tobytes()
            except:
                return self.show_PoliteCat()

    def get_available_cams(self):
        finalInt = 0
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap is None or not cap.isOpened():
                finalInt = i
                break
        return finalInt

    def show_PoliteCat(self):
        self.emptyImg = cv2.imread(os.path.join(
            os.path.dirname(__file__), 'testimg.jpg'))
        ret, jpg = cv2.imencode('.jpg', self.emptyImg)
        return jpg.tobytes()

# Generate frames from OPENCV video object
def gen(camera: Video, userid, seqid, camInt, seqstep, landmark_angles):
    # If the camera is not available for the given camInt, return a picture of polite cat
    # print("DEBUG:::", str(camera.video), str(camera.video.isOpened()))
    if camera.camInt != camInt:
        camera.set_camera(camInt)
    if not camera.video.isOpened():
        camera.video.open(camera.camInt)
    if camera.video is None or not camera.video.isOpened():
        while True:
            frame = camera.get_frame_no_pose()
            yield (b'--frame\r\n'
                   b'Content-Type:  image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    # If the camera is available for the given camInt, run the Pose Estimation methods
    else:
        camera.writeToMem_session([seqid, seqstep],f'session_user_{userid}')
        # Always Running
        n_seqid = seqid
        n_seqstep = int(seqstep)
        startTime = time.time()
        nTime = 0
        pTime = 0
        camera.startTime = time.time()
        camera.pTime = 0
        while True:
            nTime = math.floor(time.time() - startTime)
            if not camera.video.isOpened():
                break
            else:
                # the Frame is taken from the video object w/ landmark angles & name of pose
                frame = camera.get_frame(
                    {'landmark_angles': landmark_angles,
                        'poseName': f'{userid}_{n_seqid}_{n_seqstep}'}
                )
                # Return byte string of frame as image type
                yield (b'--frame\r\n'
                    b'Content-Type:  image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            # Every 2 seconds, read the memory session table and update the current seqId and seqStep
            if nTime - pTime >= 2:
                nSession = camera.readMem_session(userid)
                n_seqid = nSession[0]
                n_seqstep = nSession[1]
                # print("RUNNING SESSION:",userid,n_seqid,n_seqstep)
                pTime = nTime

def gen_no_pose(camera, camInt: int):
    camera.set_camera(camInt)
    while True:
        frame = camera.get_frame_no_pose()
        yield (b'--frame\r\n'
               b'Content-Type:  image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
