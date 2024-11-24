"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SequenceModel = void 0;
class SequenceModel {
    constructor(db) {
        this.db = db;
    }
    /**
     * Get sequence data from the 'sequence' table given a sequenceId
     * @param sequenceId Sequence ID to query.
     * @param callback Run upon successful query.
     */
    get_sequence_from_sequenceId(sequenceId) {
        return new Promise((resolve, reject) => {
            this.db.get(`SELECT * FROM sequence WHERE sequenceId = ${sequenceId};`, (err, row) => {
                if (err)
                    return reject(err);
                resolve(row);
            });
        });
    }
}
exports.SequenceModel = SequenceModel;
