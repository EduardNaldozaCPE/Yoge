"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PoseModel = void 0;
class PoseModel {
    constructor(db) {
        this.db = db;
    }
    /**
     * Get each step/pose from the 'pose' table given a sequenceId
     * @param sequenceId Sequence ID used to query pose data from.
     * @param callback Run upon succesful query.
     */
    get_steps_from_sequenceId(sequenceId) {
        return new Promise((resolve, reject) => {
            this.db.all(`SELECT * FROM pose WHERE sequenceId = ${sequenceId};`, (err, rows) => {
                if (err)
                    reject("Invalid Session Id in _get_steps_from_session");
                resolve(rows);
            });
        });
    }
}
exports.PoseModel = PoseModel;
