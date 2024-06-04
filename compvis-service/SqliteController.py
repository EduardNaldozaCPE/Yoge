import sqlite3

DBPATH = "../score-data/yoge.db"

# Processes the PoseLandmarkerResult Queue to insert into the database   
class SqliteController:
    # Initialise scores queue and sqlite connection
    def __init__(self):
        self.con = sqlite3.connect(DBPATH)
        self.cur = self.con.cursor()        


    def runInsert(self, query:str):
        # Create a new row in the session table once ScoreQueue object is created
        self.cur.execute(query)
        self.con.commit()

    def closeConnection(self):
        self.con.close()
        