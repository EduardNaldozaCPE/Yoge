from sqlite_controller import SqliteController as db
import sys

class LandmarkerSession:
    """ Stores Landmarker Session Details """
    def __init__(self, userId:int, sequenceId:int, sessionId:int):
        self.userId = userId
        self.sequenceId = sequenceId
        self.sessionId = sessionId

        # Set Session Data in Database
        self.db = db()
        self.db.runInsert(f"""
            INSERT INTO session (sessionId, userId, sequenceId) 
            VALUES ({self.sessionId}, {self.userId}, {self.sequenceId});
        """)


    def validateSession(self, closeUponValidate=True) -> bool: 
        """ Check the validity of the currently created session from the database """
        _poseList = self.db.runSelectAll(f"SELECT * FROM pose WHERE sequenceId={self.sequenceId};")
        _sessionId_res = self.db.runSelectOne(f"SELECT MAX(sessionId) FROM session;")
        if len(_poseList) == 0:
            print("Unsuccessful poseList Query @ setSessionData", file=sys.stderr)
            return False
        if len(_sessionId_res) == 0:
            print("Unsuccessful sessionId Query @ setSessionData", file=sys.stderr)
            return False
        
        if closeUponValidate: self.db.closeConnection()
        return True
