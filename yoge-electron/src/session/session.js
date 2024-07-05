const cv = require('./opencv/opencv.js');
const FrameConsumer = require("../frame_consumer/FrameConsumer.js");

const fc = new FrameConsumer("framePipe");
var currentFrame = Buffer("", "utf-8");

fc.connect();
try {
    currentFrame = fc.getFrame(); // TODO -- Loop this.
} catch (error) {
    console.log(error);
    fc.disconnect();
} finally {
    delete fc;
}

console.log("Current Frame: ");
console.log(currentFrame);

// TODO:
//  Install opencv to decode bytes to string (Refer to https://www.youtube.com/watch?v=qexy4Ph66JE&list=LL&index=1&t=509s) 
//  Use ./framebytes as a test (via fs streaming)