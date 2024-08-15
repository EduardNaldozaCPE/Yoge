"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SessionModel = void 0;
const sqlite = __importStar(require("sqlite3"));
const config_1 = require("../config");
const sqlite3 = sqlite.verbose();
class SessionModel {
    constructor() {
        this.db = new sqlite3.Database(config_1.landmarkerConfig.DB_PATH);
        this._lastScore = {
            scoreId: 0,
            sessionId: 0,
            step: 0,
            leftElbow: 0,
            rightElbow: 0,
            leftKnee: 0,
            rightKnee: 0,
            leftShoulder: 0,
            rightShoulder: 0,
            leftHip: 0,
            rightHip: 0
        };
    }
    /**
     * Get the latest score entry from the 'score' table
     * @param callback Run upon successful query.
     */
    get_latest_score(callback) {
        this.db.get("SELECT * FROM score WHERE scoreId=(SELECT MAX(scoreId) FROM score);", (err, row) => {
            let status;
            // Check for query errors 
            if (err) {
                throw Error("Error while querying _get_latest_score: " + err);
            }
            // Validate Data
            if (row !== undefined) {
                let rows2check = [
                    "scoreId", "sessionId", "step",
                    "leftElbow", "rightElbow", "leftKnee",
                    "rightKnee", "leftShoulder", "rightShoulder",
                    "leftHip", "rightHip"
                ];
                for (let i = 0; i < rows2check.length; i++) {
                    try {
                        if (row[rows2check[i]] !== undefined)
                            continue;
                    }
                    catch (e) {
                        throw Error("Error while validating _get_latest_score: " + e);
                    }
                }
                status = 'success';
                this._lastScore = row;
            }
            else {
                status = "empty";
            }
            // Call callback and set the backup
            callback(status, row);
        });
    }
    /**
     * Get each step/pose from the 'pose' table given a sequenceId
     * @param sequenceId Sequence ID used to query pose data from.
     * @param callback Run upon succesful query.
     */
    get_steps_from_sequenceId(sequenceId, callback) {
        this.db.all(`SELECT * FROM pose WHERE sequenceId = ${sequenceId};`, (err, rows) => {
            let status;
            if (err)
                throw Error("Invalid Session Id in _get_steps_from_session");
            if (rows !== undefined) {
                status = 'success';
            }
            else {
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
    get_sequence_from_sequenceId(sequenceId, callback) {
        this.db.get(`SELECT * FROM sequence WHERE sequenceId = ${sequenceId};`, (err, row) => {
            let status;
            if (err)
                throw Error("Invalid Sequence Id in _get_sequence_from_sequenceId");
            if (row !== undefined) {
                status = 'success';
            }
            else {
                status = 'empty';
            }
            callback(status, row);
        });
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
    get_all_history(callback) {
        this.db.all(`SELECT * FROM history;`, (err, rows) => {
            let status;
            if (err)
                throw Error(`Invalid Session Id in _get_steps_from_session: ${err}`);
            if (rows !== undefined) {
                status = 'success';
            }
            else {
                status = 'empty';
            }
            callback(status, rows);
        });
    }
    get_history_from_sequenceId(sequenceId, callback) {
        this.db.all(`SELECT * FROM history where sessionId IN (SELECT sessionId FROM session WHERE sequenceId=${sequenceId});`, (err, rows) => {
            let status;
            if (err)
                throw Error(`Invalid Sequence Id in get_history_from_sequenceId: ${err}`);
            if (rows !== undefined) {
                status = 'success';
            }
            else {
                status = 'empty';
            }
            callback(status, rows);
        });
    }
    get_scores_from_sequenceId(sequenceId, callback) {
        this.db.all(`SELECT * FROM score WHERE sessionId IN (SELECT sessionId FROM session WHERE sequenceId = ${sequenceId});`, (err, rows) => {
            let status;
            if (err)
                throw Error(`Invalid Sequence Id in get_scores_from_sequenceId: ${err}`);
            if (rows !== undefined) {
                status = 'success';
            }
            else {
                status = 'empty';
            }
            callback(status, rows);
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
exports.SessionModel = SessionModel;
