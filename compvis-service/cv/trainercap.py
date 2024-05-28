# Written by Eduard Naldoza, Bachelor of Science in Computer Engineering
# De La Salle University - Dasmariñas (2022)
# https://github.com/EduardNaldozaCPE/yogaposeestim-Thesis


import cv2
import time
from . import estimator as pm
import math
import os.path
from sqlite3 import Connection, Cursor
import csv
from pathlib import Path

def getScore_OLD(a, a2):
    a1 = a2 - 10
    a3 = a2 + 10
    # print(a, a1, a2, a3)
    if a3 >= 360:
        a3 -= 360
        if a <= a3:
            return 100
        elif a >= a3 and a < a1:
            return 0
        elif a >= a1 and a <= 360:
            return 100
        else:
            return 20
    elif a1 < 0:
        a1 += 360
        if a >= a1:
            return 100
        elif a <= a1 and a > a3:
            return 0
        elif a <= a3 and a >= 0:
            return 100
        else:
            return 20
    else:
        if a <= a3 and a >= a1:
            return 100
        else:
            return 0
            
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


class Video(object):
    def __init__(self, userId, sessionId, conn: Connection, c: Cursor, imgFileName:str = 'testimg.jpg', camInt = 1):
        self.sessionId = sessionId
        self.pTime = 0                      # Time of previous frame
        self.startTime = time.time()
        if type(camInt) == int:
            print('Video using camera')
            self.camInt = camInt
        elif type(camInt) == str:
            print('Video using file')
            self.camInt = f'cv/dataset/{camInt}'
        self.video = cv2.VideoCapture(self.camInt)    # OpenCV video capture
        if type(camInt) == str:
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(self.video.isOpened(), type(self.video))
        self.detector = pm.poseDetector()   # PoseModule Pose Detector object
        self.imgFileName = f'./cv/dataset/{imgFileName}'
        self.running = False
        self.seqId = None
        self.seqStep = None
        self.userId = userId
        self.conn = conn
        self.c = c
        self.csvFile = None

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
            self.c.execute(f"""
            CREATE TABLE IF NOT EXISTS sessions (
            userId INTEGER, seqId INTEGER, seqStep INTEGER
            );
            """)
        # INSERT / UPDATE SPECIFIED ROW
        with self.conn:
            # 1. CHECK IF THE SEQUENCE AND STEP IS ALREADY LOGGED
            self.c.execute(f"""SELECT * FROM sessions WHERE userId={userId}""")
            
            # 2a. IF IT DOESN'T EXIST, CREATE A NEW ROW WITH VALUES
            if len(self.c.fetchall()) == 0:
                print(f'\nNo row for userId = {userId}\nInserting new row in sessions')
                self.c.execute(f"""
                    INSERT INTO sessions
                    VALUES ({userId}, {seqId}, {seqStep});
                    """)
                    
            # 2b. IF IT ALREADY EXISTS, UPDATE THW ROW
            else:
                print(f'Row Exists\nUpdating row in sessions for userId={userId}')
                self.c.execute(f"""
                    UPDATE sessions
                    SET seqId={seqId}, seqStep={seqStep}
                    WHERE userId = {userId};
                    """)
    
    def writeToMem(self, conn: Connection, c: Cursor, s: list, fn: str):
        n_fn = fn.split('_')
        userId = n_fn[0]
        seqId = n_fn[1]
        seqStep = n_fn[2]
        # print(f"{seqId}, {seqStep}, {s[0]}, {s[1]}, {s[2]}, {s[3]}, {s[4]}, {s[5]}")
        # CREATE IN MEMORY TABLE IF IT DOES NOT ALREADY EXIST
        with conn:
            c.execute(f"""CREATE TABLE IF NOT EXISTS session_user_{userId} (
                seqId INTEGER, seqStep INTEGER, leftElbow REAL, rightElbow REAL, leftKnee REAL, rightKnee REAL, leftHip REAL, rightHip REAL
            );""")
        # INSERT / UPDATE SPECIFIED ROW
        with conn:
            # 1. CHECK IF THE SEQUENCE AND STEP IS ALREADY LOGGED
            c.execute(f"""SELECT seqId, seqStep FROM session_user_{userId} WHERE seqId = {seqId} AND seqStep = {seqStep}""")
            
            # 2a. IF IT DOESN'T EXIST, CREATE A NEW ROW WITH VALUES
            if len(c.fetchall()) == 0:
                print(f'\nNo row with seqId = {seqId} AND seqStep = {seqStep}\nInserting new row in session_user_{userId}')
                c.execute(f"""
                    INSERT INTO session_user_{userId}
                    VALUES ({seqId}, {seqStep}, {s[0]}, {s[1]}, {s[2]}, {s[3]}, {s[4]}, {s[5]});
                    """)
                    
            # 2b. IF IT ALREADY EXISTS, UPDATE THW ROW
            else:
                print(f'Row Exists\nUpdating row in session_user_{userId}')
                c.execute(f"""
                    UPDATE session_user_{userId}
                    SET leftElbow={s[0]}, rightElbow={s[1]}, leftKnee={s[2]}, rightKnee={s[3]}, leftHip={s[4]}, rightHip={s[5]}
                    WHERE seqId={seqId} AND seqStep={seqStep};
                    """)                

    def readMem_session(self, userId: str):
        with self.conn:
            self.c.execute(f"""
            SELECT seqId, seqStep
            FROM sessions
            WHERE userId={userId}
            """)
            return self.c.fetchone()
    
    def readScoreInMem(self, fn: str):
        n_fn = fn.split('_')
        userId = n_fn[0]
        seqId = n_fn[1]
        seqStep = n_fn[2]
        with self.conn:
            self.c.execute(f"""
            SELECT leftElbow , rightElbow , leftKnee , rightKnee , leftHip , rightHip
            FROM session_user_{userId}
            WHERE seqId={seqId} AND seqStep={seqStep}
            """)
            return self.c.fetchone()

    def get_frame_capture_angles(self, pose):
        # while True:
        nTime = math.floor(time.time() - self.startTime)
        # Get Image from video capture, use findPose to detect current pose, and get list/array of landmarks
        # and Draw landmarks
        success, self.img = self.video.read()
        self.img = self.detector.findPose(self.img)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255,0,255)
        thickness = 2
        self.img = cv2.putText(self.img, str(pose['poseName'])+'CAPPING',(100,100),font,fontScale,color,thickness,cv2.LINE_AA)
        self.lmList = self.detector.getLandmarks(self.img)

        # Calculate angle of each important landmark, calculate score, and write scores to CSV
        # try:
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

            if nTime - self.pTime >= 2:
                self.pTime = nTime
                

            k = cv2.waitKey(0)
            if k:
                currSession = self.readMem_session(self.userId)
                if k == ord('s'):
                    try:
                        print('creating csv file...')
                        with open(Path(__file__).parent.joinpath('dataset').joinpath(f'{pose["poseName"]}.csv'), 'x', encoding='UTF-8') as f:
                            w = csv.writer(f)
                            row = ['angle_le', 'angle_re', 'angle_lk', 'angle_rk', 'angle_lh', 'angle_rh']
                            w.writerow(row)
                    except FileExistsError:
                        print('csv file exists...')
                    with open(Path(__file__).parent.joinpath('dataset').joinpath(f'{pose["poseName"]}.csv'), 'a', encoding='UTF-8') as file:
                        w = csv.writer(file)
                        row = [self.angle_le, self.angle_re, self.angle_lk, self.angle_rk, self.angle_lh, self.angle_rh]
                        w.writerow(row)
                elif k == ord('a'):
                    self.writeToMem_session([currSession[0],(currSession[1]-1)], f'session_user_{self.userId}')
                elif k == ord('d'):
                    self.writeToMem_session([currSession[0],(currSession[1]+1)], f'session_user_{self.userId}')


            # Return final image as Byte string
            # ret, jpg = cv2.imencode('.jpg', self.img)
            # return jpg.tobytes()
        cv2.imshow(pose['poseName'], self.img)

    def get_frame_test(self, pose):
        # while True:
        nTime = math.floor(time.time() - self.startTime)
        # Get Image from video capture, use findPose to detect current pose, and get list/array of landmarks
        # and Draw landmarks
        success, self.img = self.video.read()
        self.img = self.detector.findPose(self.img)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255,0,255)
        thickness = 2
        # self.img = cv2.putText(self.img, str(pose['poseName'])+'CAPPING',(100,100),font,fontScale,color,thickness,cv2.LINE_AA)
        self.lmList = self.detector.getLandmarks(self.img)

        # Calculate angle of each important landmark, calculate score, and write scores to CSV
        # try:
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

            # Calculate Score
            self.scores = []
            # print('GETSCORE:', self.angle_le, pose['landmark_angles'][0][0])
            self.scores.append(
                getScore(self.angle_le, pose['landmark_angles'][0][0]))
            self.scores.append(
                getScore(self.angle_re, pose['landmark_angles'][0][1]))
            self.scores.append(
                getScore(self.angle_lk, pose['landmark_angles'][0][2]))
            self.scores.append(
                getScore(self.angle_rk, pose['landmark_angles'][0][3]))
            self.scores.append(
                getScore(self.angle_lh, pose['landmark_angles'][0][4]))
            self.scores.append(
                getScore(self.angle_rh, pose['landmark_angles'][0][5]))

            self.img = cv2.putText(self.img, str(pose['landmark_angles'][0][1]), (100,200), font, fontScale, color, thickness, cv2.LINE_AA)
            self.img = cv2.putText(self.img, str(self.scores[1]), (100,100), font, fontScale, color, thickness, cv2.LINE_AA)

            for i_score, score in enumerate(self.scores):
                limb = []
                if i_score == 0: limb = [11, 13, 15]
                if i_score == 1: limb = [12, 14, 16]
                if i_score == 2: limb = [23, 25, 27]
                if i_score == 3: limb = [24, 26, 28]
                if i_score == 4: limb = [11, 23, 25]
                if i_score == 5: limb = [12, 24, 26]
                if score > 75:
                    self.img = self.detector.highlightLimb(self.img, limb[0], limb[1])
                    self.img = self.detector.highlightLimb(self.img, limb[1], limb[2])

            if nTime - self.pTime >= 2:
                self.pTime = nTime

            k = cv2.waitKey(25)

        cv2.imshow(pose['poseName'], self.img)

    def get_frame_capture_angles_img(self, pose):
        # while True:
        nTime = math.floor(time.time() - self.startTime)
        # Get Image from video capture, use findPose to detect current pose, and get list/array of landmarks
        # and Draw landmarks
        self.img = cv2.imread(self.imgFileName)
        self.img = self.detector.findPose(self.img)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255,0,255)
        thickness = 2
        self.img = cv2.putText(self.img, str(pose['poseName'])+'CAPPING',(100,100),font,fontScale,color,thickness,cv2.LINE_AA)
        self.lmList = self.detector.getLandmarks(self.img)

        # Calculate angle of each important landmark, calculate score, and write scores to CSV
        # try:
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

            # print('n', nTime)
            # print('start:', self.startTime)
            # print('p', self.pTime)
            if nTime - self.pTime >= 2:
                try:
                    print('creating csv file...')
                    with open(Path(__file__).parent.joinpath('dataset').joinpath(f'{pose["poseName"]}.csv'), 'x', encoding='UTF-8') as f:
                        w = csv.writer(f)
                        row = ['angle_le', 'angle_re', 'angle_lk', 'angle_rk', 'angle_lh', 'angle_rh']
                        w.writerow(row)
                except FileExistsError:
                    print('csv file exists...')
                with open(Path(__file__).parent.joinpath('dataset').joinpath(f'{pose["poseName"]}.csv'), 'a', encoding='UTF-8') as file:
                    w = csv.writer(file)
                    row = [self.angle_le, self.angle_re, self.angle_lk, self.angle_rk, self.angle_lh, self.angle_rh]
                    w.writerow(row)
                self.pTime = nTime
                

            # Return final image as Byte string
            # ret, jpg = cv2.imencode('.jpg', self.img)
            # return jpg.tobytes()
        cv2.imshow(pose['poseName'], self.img)

    def set_camera(self, camInt):
        self.video = cv2.VideoCapture(camInt)

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

def gen_cap(camera: Video, userid, seqid, camInt, seqstep, landmark_angles):
    # If the camera is not available for the given camInt, return a picture of polite cat
    if type(camInt) == str: camInt = f'cv/dataset/{camInt}'
    if camera.camInt != camInt:
        camera.set_camera(camInt)
        print('camInt not the same\r', camInt, camera.camInt)
    if camera.video is None:
        print('Err: Video is None')
    elif not camera.video.isOpened():
        print('Err: Video is is not Opened')

    # If the camera is available for the given camInt, run the pose Estimation methods
    else:
        camera.writeToMem_session([seqid, seqstep],f'session_user_{userid}')
        # Always Running
        n_seqid = seqid
        n_seqstep = int(seqstep)
        startTime = time.time()
        nTime = 0
        pTime = 0 
        while True:
            nTime = math.floor(time.time() - startTime)
            if not camera.video.isOpened():
                break
            else:
                camera.get_frame_capture_angles(pose={
                    'landmark_angles': landmark_angles,
                    'poseName': f'{userid}_{n_seqid}_{n_seqstep}'
                    })
            if nTime - pTime >= 2:
                nSession = camera.readMem_session(userid)
                n_seqid = nSession[0]
                n_seqstep = nSession[1]
                print("SESSION:",userid,n_seqid,n_seqstep)
                pTime = nTime

            k = cv2.waitKey(25)
            if k:    
                # currSession = camera.readMem_session(userid)
                if k == ord('q'):
                    break
                # elif k == ord('a'):
                #     camera.writeToMem_session([currSession[0],(currSession[1]-1)], f'session_user_{userid}')
                # elif k == ord('d'):
                #     camera.writeToMem_session([currSession[0],(currSession[1]+1)], f'session_user_{userid}')

def gen_test(camera: Video, userid, seqid, camInt, seqstep, landmark_angles):
    # If the camera is not available for the given camInt, return a picture of polite cat
    if camera.camInt != camInt:
        camera.set_camera(camInt)
    if camera.video is None or not camera.video.isOpened():
        print('Err')
    # If the camera is available for the given camInt, run the pose Estimation methods
    else:
        camera.writeToMem_session([seqid, seqstep],f'session_user_{userid}')
        # Always Running
        n_seqid = seqid
        n_seqstep = int(seqstep)
        startTime = time.time()
        nTime = 0
        pTime = 0 
        while True:
            nTime = math.floor(time.time() - startTime)
            if not camera.video.isOpened():
                break
            else:
                camera.get_frame_test(pose={
                    'landmark_angles': landmark_angles,
                    'poseName': f'{userid}_{n_seqid}_{n_seqstep}'
                    })
            if nTime - pTime >= 2:
                nSession = camera.readMem_session(userid)
                n_seqid = nSession[0]
                n_seqstep = nSession[1]
                print("SESSION:",userid,n_seqid,n_seqstep)
                print("ANGLES:",landmark_angles)
                pTime = nTime

       
def gen_cap_img(camera: Video, userid, seqid, camInt, seqstep, landmark_angles):
    # If the camera is not available for the given camInt, return a picture of polite cat
    if camera.camInt != camInt:
        camera.set_camera(camInt)

    if camera.video is None or not camera.video.isOpened():
        print('Err')
    # If the camera is available for the given camInt, run the pose Estimation methods
    else:
        camera.writeToMem_session([seqid, seqstep],f'session_user_{userid}')
        # Always Running
        n_seqid = seqid
        n_seqstep = int(seqstep)
        startTime = time.time()
        nTime = 0
        pTime = 0 
        while True:
            nTime = math.floor(time.time() - startTime)
            if not camera.video.isOpened():
                break
            else:
                camera.get_frame_capture_angles_img(pose={
                    'landmark_angles': landmark_angles,
                    'poseName': f'{userid}_{n_seqid}_{n_seqstep}'
                    })
            if nTime - pTime >= 2:
                nSession = camera.readMem_session(userid)
                n_seqid = nSession[0]
                n_seqstep = nSession[1]
                print("SESSION:",userid,n_seqid,n_seqstep)
                pTime = nTime

            k = cv2.waitKey(25)
            if k:    
                currSession = camera.readMem_session(userid)
                if k == ord('q'):
                    break
                elif k == ord('a'):
                    camera.writeToMem_session([currSession[0],(currSession[1]-1)], f'session_user_{userid}')
                elif k == ord('d'):
                    camera.writeToMem_session([currSession[0],(currSession[1]+1)], f'session_user_{userid}')
            
