import queue as q
from SqliteController import SqliteController as Db

# Processes the PoseLandmarkerResult Queue to insert into the database   
class ScoreQueue:
    # Initialise scores queue and sqlite connection
    def __init__(self, userId, sessionId, sequenceId = 0):
        self.userId = userId
        self.sessionId = sessionId
        self.sequenceId = sequenceId
        self.running = True
        self.scores = q.Queue()


    # Puts a new score into the queue
    def addScore(self, score):
        self.scores.put(score)


    # Processes the scores queue one-by-one.
    # NOTE -- Run in a separate thread and stop by using ScoresQueue.stopProcessing()
    def recordScores(self):
        # Create a new row in the session table once ScoreQueue object is created
        try:
            self.db = Db()
            self.db.runInsert(f"""
                INSERT INTO session (userId, sequenceId) VALUES ({self.userId}, {self.sequenceId});
                """)
        except:
            print("Encountered an error while connecting to Sqlite Db.")
            return

        # Starts processing the scores if the queue is not empty
        try:
            while self.running:
                if self.scores.empty(): continue
                lastScore = self.scores.get()

                # TODO -- INSERT THIS SCORE DATA INTO THE DATABASE
                print("Score: ", len(str(lastScore)))

                # self.cur.execute(f"""
                #     INSERT INTO score VALUES 
                #                  ({})
                #     """)
        except KeyboardInterrupt:
            print("Stopped by KeyboardInterrupt")
            self.running = False

        print("Closing Db Connection...")
        self.db.closeConnection()

    def stopProcessing(self):
        self.running = False