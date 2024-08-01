import sqlite3, json, os, sys

class SqliteController:
    """ Connects to yoge database and runs SQL queries """
    def __init__(self):
        # Initialise scores queue and sqlite connection
        config = open(os.path.join(os.getcwd(), 'resources/landmarker-config.json'), 'r')
        config_options = json.load(config)
        DB_PATH = config_options["DB_PATH"]
        config.close()
        
        self.con = sqlite3.connect(DB_PATH)
        self.cur = self.con.cursor()


    def runInsert(self, query):
        """ Run an Insert Query in the yoge database """
        if query is None: return
        try: 
            self.cur.execute(query)
            self.con.commit()
        except sqlite3.IntegrityError as e:
            print(e, file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)


    def runSelectAll(self, query):
        """ Run an Insert Query in the yoge database """
        data = []
        if query is None: return []
        try:
            res = self.cur.execute(query)
            data = res.fetchall()
        except Exception as e:
            print(e, file=sys.stderr)
        return data


    def runSelectOne(self, query): 
        """ Run an Insert Query in the yoge database """
        data = ()
        if query is None: return ()
        try:
            res = self.cur.execute(query)
            data = res.fetchone()
        except Exception as e:
            print(e, file=sys.stderr)
        return data


    def closeConnection(self):
        """ Closes the database connection """
        self.con.close()
        