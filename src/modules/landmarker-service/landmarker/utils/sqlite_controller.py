import sqlite3
import json
import os
import sys


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


    def runInsert(self, query):
        print("RUNNING INSERT:", query, file=sys.stderr)
        if query is None: return
        try: 
            self.cur.execute(query)
            self.con.commit()
        except Exception as e: 
            print(e, file=sys.stderr)


    def runSelectAll(self, query):
        data = []
        if query is None: return []
        try:
            res = self.cur.execute(query)
            data = res.fetchall()
        except Exception as e:
            print(e, file=sys.stderr)
        return data


    def runSelectOne(self, query):
        data = ()
        if query is None: return ()
        try:
            res = self.cur.execute(query)
            data = res.fetchone()
        except Exception as e:
            print(e, file=sys.stderr)
        return data


    def closeConnection(self):
        self.con.close()
        