import queue as q
import sqlite3

DBPATH = "../score-data/yoge.db"

# Processes the PoseLandmarkerResult Queue to insert into the database   
class ScoreQueue:
    # Initialise scores queue and sqlite connection
    def __init__(self, userId, sessionId, sequenceId = 0):
        self.userId = userId
        self.sessionId = sessionId
        self.sequenceId = sequenceId
        self.running = True

        self.scores = q.Queue()
        self.con = sqlite3.connect(DBPATH)
        self.cur = self.con.cursor()
        
        # Create a new row in the session table once ScoreQueue object is created
        self.cur.execute(f"""
            INSERT INTO session (userId, sequenceId) VALUES ({self.userId}, {self.sequenceId});
            """)


    # Puts a new score into the queue
    def addScore(self, score):
        self.scores.put(score)


    # Processes the scores queue one-by-one
    def processScores(self):
        # Starts processing the scores if they're the queue is not empty
        while self.running:
            if self.scores.empty(): continue

            lastScore = self.scores.get()

            # TODO -- INSERT THIS SCORE DATA INTO THE DATABASE
            print(len(str(lastScore)))
            # self.cur.execute(f"""
            #     INSERT INTO score VALUES 
            #                  ({})
            #     """)

    def stopProcessing(self):
        self.running = False