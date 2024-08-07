import * as sqlite from 'sqlite3';
import { scoreType, scoreKey, sequenceType, sequenceKey, sessionType } from '../dataTypes';
import { landmarkerConfig } from '../config';

const sqlite3 = sqlite.verbose();

export class SessionModel {
    db: sqlite.Database;
    _lastScore: scoreType;

    constructor() {
        this.db = new sqlite3.Database(landmarkerConfig.DB_PATH);
        this._lastScore = {
            scoreId       : 0,
            sessionId     : 0,
            step          : 0,
            leftElbow     : 0, 
            rightElbow    : 0, 
            leftKnee      : 0, 
            rightKnee     : 0, 
            leftShoulder  : 0, 
            rightShoulder : 0, 
            leftHip       : 0, 
            rightHip      : 0
          };
    }

    /**
     * Get the latest score entry from the 'score' table
     * @param callback Run upon successful query.
     */
    get_latest_score (callback: (status:string, data: scoreType)=>(void)): void {
        this.db.get<scoreType>(
        "SELECT * FROM score WHERE scoreId=(SELECT MAX(scoreId) FROM score);",
        (err, row)=>{
            let status;
            // Check for query errors 
            if (err) {
                throw Error("Error while querying _get_latest_score: "+err);
            }
            // Validate Data
            if (row !== undefined) {
                let rows2check: Array<scoreKey>= [
                    "scoreId", "sessionId","step",
                    "leftElbow", "rightElbow", "leftKnee", 
                    "rightKnee", "leftShoulder", "rightShoulder", 
                    "leftHip", "rightHip"
                ];
                for (let i=0; i<rows2check.length; i++) {
                    try {
                        if (row[rows2check[i]] !== undefined) continue;
                    } catch (e) {
                        throw Error("Error while validating _get_latest_score: "+e);
                    }
                }
                status = 'success';
                this._lastScore = row;
            } else {
                status = "empty"; 
            }
            // Call callback and set the backup
            callback(status, row);
        }
        );
    }
    
    
    /**
     * Get each step/pose from the 'pose' table given a sequenceId
     * @param sequenceId Sequence ID used to query pose data from.
     * @param callback Run upon succesful query.
     */
    get_steps_from_sequenceId(sequenceId: number ,callback: (status:string, rows:Array<any>) => (void)): void {
        this.db.all(`SELECT * FROM pose WHERE sequenceId = ${sequenceId};`, (err, rows)=>{
            let status;
            if (err) throw Error("Invalid Session Id in _get_steps_from_session");
            if (rows !== undefined) {
                status = 'success';
            } else {
                status = 'empty';
            }
            callback(status, rows);
        });
    }
    
    
    /**
     * Get sequence data from the 'sequence' table given a sequenceId 
     * @param sequenceId Sequence ID to query.
     * @param callback Run upon successful query.
     */
    get_sequence_from_sequenceId(sequenceId: number ,callback: (status:string, rows:sequenceType) => (void)): void {
        this.db.get(
        `SELECT * FROM sequence WHERE sequenceId = ${sequenceId};`,
        (err, row: sequenceType)=>{
            let status;
            if (err) throw Error("Invalid Sequence Id in _get_sequence_from_sequenceId");
            
            if (row !== undefined) {
                status = 'success';
            } else {
                status = 'empty';
            }
            callback(status, row);
        }
        );
    }
    
    
    /**
     * Get the latest sessionId from the 'session' table
     * @param callback Run upon successful query.
     */
    get_latest_sessionId(callback: (status:string, sequenceId: number) => (void)): void {
        this.db.get(
        `SELECT MAX(sessionId) FROM session;`,
        (err, row: sessionType)=>{
            let sequenceId: number;
            let status: string;
    
            // Check for query Errors
            if (err)
            throw Error("Error Caught _get_latest_sessionId: "+err);
    
            
            // Validate Data
            if (row !== undefined) {
                status = 'success';
            } else {
                status = 'empty';
            }
            sequenceId = row.sessionId;
    
            // Run Callback if there are no errors during validation
            callback(status, sequenceId);
        }
        );
    }

    postNewHistory(sessionId:number, score:number) {
        this.db.serialize(() => {
            this.db.run(`INSERT INTO history VALUES (${Date.now()}, ${sessionId}, ${Date.now()}, ${score})`, (err)=>{
                if (err)
                    throw new Error("Error while posting new History row");
            });
        });
    }
}