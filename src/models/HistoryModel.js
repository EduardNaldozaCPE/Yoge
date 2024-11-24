"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HistoryModel = void 0;
class HistoryModel {
    constructor(db) {
        this.db = db;
    }
    get_history_from_sequenceId(sequenceId) {
        return new Promise((resolve, reject) => {
            this.db.all(`SELECT * FROM history where sessionId IN (SELECT sessionId FROM session WHERE sequenceId=${sequenceId});`, (err, rows) => {
                if (err)
                    reject(`Invalid Sequence Id in get_history_from_sequenceId: ${err}`);
                resolve(rows);
            });
        });
    }
    get_all_history() {
        return new Promise((resolve, reject) => {
            this.db.all(`
                SELECT historyId,history.sessionId,datetime,score,session.sequenceId,sequenceName FROM history
                INNER JOIN session ON history.sessionId=session.sessionId
                LEFT JOIN sequence ON session.sequenceId = sequence.sequenceId;`, (err, rows) => {
                if (err)
                    return reject(`Invalid Session Id in _get_steps_from_session: ${err}`);
                resolve(rows);
            });
        });
    }
    postNewHistory(sessionId, score) {
        this.db.serialize(() => {
            this.db.run(`INSERT INTO history VALUES (${Date.now()}, ${sessionId}, ${Date.now()}, ${score})`, (err) => {
                if (err)
                    throw new Error(`Error while posting new History row: ${err}`);
            });
        });
    }
}
exports.HistoryModel = HistoryModel;