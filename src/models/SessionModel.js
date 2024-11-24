"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionModel = void 0;
class SessionModel {
    constructor(db) {
        this.db = db;
    }
    /**
     * Get the latest sessionId from the 'session' table
     * @param callback Run upon successful query.
     */
    get_latest_sessionId(callback) {
        this.db.get(`SELECT MAX(sessionId) FROM session;`, (err, row) => {
            let sequenceId;
            let status;
            // Check for query Errors
            if (err)
                throw Error("Error Caught _get_latest_sessionId: " + err);
            // Validate Data
            if (row !== undefined) {
                status = 'success';
            }
            else {
                status = 'empty';
            }
            sequenceId = row.sessionId;
            // Run Callback if there are no errors during validation
            callback(status, sequenceId);
        });
    }
}
exports.SessionModel = SessionModel;
