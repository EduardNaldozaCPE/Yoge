const net = require('node:net');

module.exports = class FrameConsumer {
    constructor(pipeName) {
        this.pipeDir = "\\\\.\\pipe\\&".replace('&',pipeName)
        this.currentFrame;
        this.client = undefined;
    }

    connect() {
        console.log(`Connecting to pipe: ${this.pipeDir}`);

        this.client = net.createConnection( `${this.pipeDir}`, () => {
            console.log("Connected to named pipe.");
        });

        this.client.on('data', (data) => {
            console.log(data.length());
            this.currentFrame = data;
        });

        this.client.on('end', ()=>console.log("Disconnecting from the named pipe."));

    }

    disconnect() {
        console.log("Disconnecting from the named pipe.");
        this.client.end((err) => {
            if (err) {
                throw Error(`Encountered error while attempting to disconnect from the named pipe: ${err}`);
            }
        });
    }

    getFrame() {
        return this.currentFrame;
    }
};