// UNUSED (might not have been a good idea. Leaving this file here just in case)

import { spawn, ChildProcess } from 'node:child_process'
export class LandmarkerAPI {
    landmarker: ChildProcess | null;
    command: string;
    args: Array<string>;
    debug: boolean;
    constructor(command:string, args:Array<string>=[], debug=false) {
        this.landmarker = null;
        this.command = command;
        this.debug = debug;
        this.args = args;
    }

    /**
     * Start the landmarker.
     */
    start(): void {
        this.landmarker = spawn(this.command, this.args);

        if (!this.isInstanceExists())
            throw new Error("Landmarker could not start.");
        
        // TODO -- Move functionality here
        this.landmarker!.stdout!.on('data', (data)=>{

        });

        this.landmarker!.stderr!.on('data', ()=>{

        });

        this.landmarker!.stdout!.on('data', ()=>{
            
        });
    }

    /**
     * Check if this instance exists
     * @returns Returns `true` if the landmarker is a ChildProcess and is not killed
     */
    isInstanceExists(): boolean {
        return this.landmarker instanceof ChildProcess && !this.landmarker.killed
    }
    
}