import * as sqlite from 'sqlite3';
import { scoreKey, sequenceType, sessionType } from '../dataTypes';

export class SessionModel {
    db: sqlite.Database;

    constructor(db: sqlite.Database) {
        this.db = db;
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
}