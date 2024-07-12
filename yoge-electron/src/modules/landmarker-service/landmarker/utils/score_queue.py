import queue as q
from .sqlite_controller import SqliteController as Db
import mediapipe as mp 

JOINT_IDS = {
    "leftShoulder"  : 11,
    "rightShoulder" : 12,
    "leftElbow"     : 13,
    "rightElbow"    : 14,
    "leftHip"       : 23,
    "rightHip"      : 24,
    "leftKnee"      : 25,
    "rightKnee"     : 26,
}

# Processes the PoseLandmarkerResult Queue to insert into the database   
class ScoreQueue:
    # Initialise scores queue and sqlite connection
    def __init__(self, userId, sessionId, sequenceId = 0):
        self.userId = userId
        self.sessionId = sessionId
        self.sequenceId = sequenceId
        self.running = False
        self.scores = q.Queue()
        self.filteredScores = q.Queue()


    # Puts a new score into the queue
    def addScore(self, score, timestamp):
        self.scores.put({"score":score, "timestamp":timestamp})


    # Processes the scores queue one-by-one.
    # NOTE -- Run in a separate thread and stop by using ScoresQueue.stopProcessing()
    def recordScores(self):
        # Create a new row in the session table once ScoreQueue object is created
        try:
            self.db = Db()
        except:
            print("Encountered an error while connecting to Sqlite Db.")
            return
        
        self.db.runInsert(f"""
            INSERT INTO session (userId, sequenceId) VALUES ({self.userId}, {self.sequenceId});
            """)
        self.running = True

        # Starts processing the scores if the queue is not empty
        while self.running:
            if self.scores.empty(): continue

            # TODO -- PROCESS THESE RAW COORDS TO SCORE. rn it is just recording the x-coordinates of each limb
            lastRecord = self.scores.get()
            lastScore = lastRecord["score"]
            timestamp = lastRecord["timestamp"]

            filteredScore:dict = {}
            if type(lastScore) is mp.tasks.vision.PoseLandmarkerResult:
                try:
                    for key in JOINT_IDS:
                        filteredScore[key] = {}
                        filteredScore[key]['x'] = lastScore.pose_landmarks[0][JOINT_IDS[key]].x
                        filteredScore[key]['y'] = lastScore.pose_landmarks[0][JOINT_IDS[key]].y
                        filteredScore[key]['z'] = lastScore.pose_landmarks[0][JOINT_IDS[key]].z

                    self.db.runInsert(f"""
                        INSERT INTO score (sessionId, timestamp, leftElbow, rightElbow, leftKnee, rightKnee, leftShoulder, rightShoulder, leftHip, rightHip) VALUES 
                                    (
                                    {self.sessionId}, 
                                    {timestamp}, 
                                    {filteredScore["leftElbow"]["x"]}, 
                                    {filteredScore["rightElbow"]["x"]}, 
                                    {filteredScore["leftKnee"]["x"]}, 
                                    {filteredScore["rightKnee"]["x"]}, 
                                    {filteredScore["leftShoulder"]["x"]}, 
                                    {filteredScore["rightShoulder"]["x"]}, 
                                    {filteredScore["leftHip"]["x"]}, 
                                    {filteredScore["rightHip"]["x"]}
                                    );
                        """)
                except IndexError as e:
                    print("Landmarks incomplete. Skipping.")
        
        self.running = False
        print("db Connection Closing...")
        self.db.closeConnection()
        print("db Connection Closed.")

    def stopProcessing(self):
        self.running = False