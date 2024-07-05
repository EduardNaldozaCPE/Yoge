// const cv = require('../opencv/opencv.js');
const net = require('node:net');

const BUFFERSIZE = 1048576;
const PIPEDIR = "\\\\.\\pipe\\framePipe";
const connectionListener = () => {
    console.log("Successfully Connected.");
}

// TODO:
//  - Run main() on one thread, use currentFrame to store the current frame.
// Other:
//  - Handle ENOENT when named pipe isn't created.
//  - Install opencv to decode bytes to string (Refer to https://www.youtube.com/watch?v=qexy4Ph66JE&list=LL&index=1&t=509s) 

var currentFrame = Buffer.alloc(BUFFERSIZE, "\x01", 'utf-8');
const liveFeed = document.getElementById("live-feed");
if (liveFeed) {
    setInterval(() => {
        //  TODO -- Run interval on updating the live feed (use current frame every 30ms).
    }, 1000);
}

function main() {
    // 1. Connect to named pipe using 'node:net'
    console.log(`Connecting to named pipe: ${PIPEDIR}`);
    try {
        var client = net.createConnection( `${PIPEDIR}`, connectionListener);
    } catch (error) {
        console.log(`Encountered an error while connecting: \n${error}`);
    }

    
    client.on('data', (data) => {
        // Handle on data.
        console.log(data.length);
        currentFrame = data;
    });
    

    client.on('end', () => {
        // Handle on end.
        console.log("Disconnecting from the named pipe.");
    });
    
    function disconnect() {
        console.log("Disconnecting from the named pipe.");
        client.end((err) => {
            if (err) {
                console.log(`Encountered error while attempting to disconnect from the named pipe: ${err}`);
            }
        });
    }
}

main();