"use strict";
// UNUSED (might not have been a good idea. Leaving this file here just in case)
Object.defineProperty(exports, "__esModule", { value: true });
exports.LandmarkerAPI = void 0;
const node_child_process_1 = require("node:child_process");
class LandmarkerAPI {
    constructor(spawncommand, args = [], debug = false) {
        this.landmarker = null;
        this.spawncommand = spawncommand;
        this.debug = debug;
        this.args = args;
    }
    /**
     * Start the landmarker.
     */
    start() {
        this.landmarker = (0, node_child_process_1.spawn)(this.spawncommand, this.args);
        if (!this.isInstanceExists())
            throw new Error("Landmarker could not start.");
    }
    /**
     * Check if this instance exists
     * @returns Returns `true` if the landmarker is a ChildProcess and is not killed
     */
    isInstanceExists() {
        return this.landmarker instanceof node_child_process_1.ChildProcess && !this.landmarker.killed;
    }
    /**
     * Assigns the callback upon retrieval of frame data
     * @param callback Calls upon retrieval of data
     */
    onData(callback) {
        if (!this.isInstanceExists()) {
            console.error("No Landmarker");
        }
        this.landmarker.stdout.on('data', (data) => {
            callback(data);
        });
    }
    /**
     * Assigns the callback upon reading stderr
     * @param on_next_pose Calls upon NPOSE signal
     * @param on_stderr Calls upon stderr
     */
    onCommand(on_next_pose = (data) => { }, on_stderr = (data) => { }, on_stop_vid = () => { }) {
        if (!this.isInstanceExists()) {
            console.error("No Landmarker");
        }
        this.landmarker.stderr.on('data', (data) => {
            let prefix = data.toString().substring(0, 5);
            let suffix = data.toString().substring(data.length - 5, data.length);
            if (prefix == "NPOSE" || suffix == "NPOSE") {
                on_next_pose(data);
            }
            else if (prefix == "NOVID" || suffix == "NOVID") {
                this.send_command("novid");
            }
            else if (prefix == "STPRC" || suffix == "STPRC") {
                on_stop_vid();
            }
            else {
                on_stderr(data);
            }
        });
    }
    /**
     * Assigns the callback upon child termination
     * @param on_normal_close Calls upon '0' exit
     * @param on_novideo_close Calls upon '1' exit
     */
    onClose(on_normal_close, on_novideo_close) {
        if (!this.isInstanceExists()) {
            console.error("No Landmarker");
        }
        this.landmarker.on('close', (code, signal) => {
            switch (code) {
                case null: break;
                case 0:
                    on_normal_close();
                    break;
                case 1:
                    on_novideo_close();
                    break;
                default:
                    console.log("Landmarker closed with code: ", code);
                    break;
            }
        });
    }
    /**
     * Kills the landmarker child process
     */
    kill() {
        if (this.landmarker instanceof node_child_process_1.ChildProcess) {
            this.landmarker.kill();
            this.landmarker = null;
        }
    }
    /**
     * Sends a command to the landmarker
     * @param command Command to send to landmarker
     */
    send_command(command) {
        try {
            if (this.landmarker instanceof node_child_process_1.ChildProcess) {
                this.landmarker.stdin.write(`${command}\n`);
                console.log("SENT COMMAND: " + command);
            }
        }
        catch (e) {
            console.log("Error while sending to landmarker: ", e);
        }
    }
}
exports.LandmarkerAPI = LandmarkerAPI;
