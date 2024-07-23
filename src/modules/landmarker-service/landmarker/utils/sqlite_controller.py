import sqlite3
import json
import os


# Processes the PoseLandmarkerResult Queue to insert into the database   
class SqliteController:
    # Initialise scores queue and sqlite connection
    def __init__(self):
        config = open(os.path.join(os.getcwd(), 'resources/landmarker-config.json'), 'r')
        config_options = json.load(config)
        DB_PATH = config_options["DB_PATH"]
        config.close()
        
        self.con = sqlite3.connect(DB_PATH)
        self.cur = self.con.cursor()


    def runInsert(self, query:str):
        # Create a new row in the session table once ScoreQueue object is created
        if query is None: return 
        try: 
            self.cur.execute(query)
            self.con.commit()
        except Exception as e: 
            print(e)


    def closeConnection(self):
        self.con.close()
        