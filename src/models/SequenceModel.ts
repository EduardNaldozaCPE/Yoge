import * as sqlite from 'sqlite3';
import { sequenceType, sessionType } from '../dataTypes';

export class SequenceModel {
    db: sqlite.Database;

    constructor(db: sqlite.Database) {
        this.db = db;
    }    
    
    /**
     * Get sequence data from the 'sequence' table given a sequenceId 
     * @param sequenceId Sequence ID to query.
     * @param callback Run upon successful query.
     */
    get_sequence_from_sequenceId(sequenceId: number): Promise<sequenceType> {
        return new Promise((resolve, reject)=>{
            this.db.get(
                `SELECT * FROM sequence WHERE sequenceId = ${sequenceId};`,
                (err, row: sequenceType)=>{
                    if (err) return reject(err);
                    resolve(row);
                }
            );
        })
    }
}