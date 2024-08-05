"use strict";
// UNUSED (might not have been a good idea. Leaving this file here just in case)
Object.defineProperty(exports, "__esModule", { value: true });
exports.LandmarkerAPI = void 0;
const node_child_process_1 = require("node:child_process");
class LandmarkerAPI {
    constructor(command, args = [], debug = false) {
        this.landmarker = null;
        this.command = command;
        this.debug = debug;
        this.args = args;
    }
    /**
     * Start the landmarker.
     */
    start() {
        this.landmarker = (0, node_child_process_1.spawn)(this.command, this.args);
        if (!this.isInstanceExists())
            throw new Error("Landmarker could not start.");
        // TODO -- Move functionality here
        this.landmarker.stdout.on('data', (data) => {
        });
        this.landmarker.stderr.on('data', () => {
        });
        this.landmarker.stdout.on('data', () => {
        });
    }
    /**
     * Check if this instance exists
     * @returns Returns `true` if the landmarker is a ChildProcess and is not killed
     */
    isInstanceExists() {
        return this.landmarker instanceof node_child_process_1.ChildProcess && !this.landmarker.killed;
    }
}
exports.LandmarkerAPI = LandmarkerAPI;
