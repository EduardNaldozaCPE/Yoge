const net = require('node:net');

module.exports = class FrameConsumer {
    /**
     * Connects to a named pipe using 'node:net' and stores the contents in state.
     * @param {string} pipeName Name of the Named Pipe in the \\.pipe\<pipeName> directory.
     */
    constructor(pipeName) {
        this.pipeDir = "\\\\.\\pipe\\&".replace('&',pipeName)
        this.currentFrame;
        this.client = undefined;
    }

    /**
     * Connects to the Named Pipe.
     */
    connect() {
        console.log(`Connecting to named pipe: ${this.pipeDir}`);

        this.client = net.createConnection( `${this.pipeDir}`, () => {
            console.log("Successfully Connected.");
        });

        this.client.on('data', (data) => {
            console.log(data.length());
            this.currentFrame = data;
        });

        this.client.on('end', ()=>console.log("Disconnecting from the named pipe."));

    }

    /**
     * Stops the connection to the named pipe.
     */
    disconnect() {
        console.log("Disconnecting from the named pipe.");
        this.client.end((err) => {
            if (err) {
                throw Error(`Encountered error while attempting to disconnect from the named pipe: ${err}`);
            }
        });
    }

    /**
     * Gets the current frame stored in state.
     * @returns the current frame stored in state.
     */
    getFrame() {
        return this.currentFrame;
    }
};