import * as sqlite from 'sqlite3';

export class PoseModel {
    db: sqlite.Database;

    constructor(db: sqlite.Database) {
        this.db = db;
    }

    /**
     * Get each step/pose from the 'pose' table given a sequenceId
     * @param sequenceId Sequence ID used to query pose data from.
     * @param callback Run upon succesful query.
     */
    get_steps_from_sequenceId(sequenceId: number): Promise<Array<any>> {
        return new Promise((resolve, reject)=>{
            this.db.all(`SELECT * FROM pose WHERE sequenceId = ${sequenceId};`, (err, rows)=>{
                if (err) reject("Invalid Session Id in _get_steps_from_session");
                resolve(rows);
            });
        });
    }
} 