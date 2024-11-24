import * as sqlite from 'sqlite3';
import { scoreKey, sequenceType, sequenceKey, sessionType } from '../dataTypes';
import { landmarkerConfig } from '../config';

export class ScoreModel {
    db: sqlite.Database;
    _lastScore: Score;

    constructor(db: sqlite.Database) {
        this.db = db;
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
    get_latest_score(): Promise<Score> {
        return new Promise((resolve, reject)=>{
            this.db.get<Score>(
            "SELECT * FROM score WHERE scoreId=(SELECT MAX(scoreId) FROM score);",
            (err, row)=>{
                // Check for query errors 
                if (err) return reject(err)

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
                    this._lastScore = row;
                } else {
                    return reject("Empty"); 
                }

                // Call callback and set the backup
                resolve(row);
            }
            );
        });
    }
    
    get_scores_from_sequenceId(sequenceId:number): Promise<Array<any>> {
        return new Promise((resolve, reject)=>{
            this.db.all(`SELECT * FROM score WHERE sessionId IN (SELECT sessionId FROM session WHERE sequenceId = ${sequenceId});`,
                (err, rows)=>{
                    if (err) reject(`Invalid Sequence Id in get_scores_from_sequenceId: ${err}`);
                    resolve(rows);
                }
            )
        })
    }
}