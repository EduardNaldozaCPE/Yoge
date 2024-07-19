import sqlite3
import json


# Processes the PoseLandmarkerResult Queue to insert into the database   
class SqliteController:
    # Initialise scores queue and sqlite connection
    def __init__(self):
        config = open('./landmarker-config.json', 'r')
        config_options = json.load(config)
        DBPATH = config_options["DBPATH"]
        config.close()
        
        self.con = sqlite3.connect(DBPATH)
        self.cur = self.con.cursor()


    def runInsert(self, query:str):
        # Create a new row in the session table once ScoreQueue object is created
        self.cur.execute(query)
        self.con.commit()


    def closeConnection(self):
        self.con.close()
        