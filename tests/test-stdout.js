const { spawn } = require("child_process");

const producer = spawn('python', ['landmarker-service/main.py', '-user=0', '-sequence=1', '-session=2']);

var outCount = 0;

producer.stdout.on('data', (data)=>{
    outCount++;
    strData = data.toString().substring(0, 15);
    console.log(`[${outCount}] out: ${strData}`);
});

producer.stderr.on('data', (data)=>{
    console.log(`${data}`);
});

producer.on('close', (code, signal)=>{
    if (code) console.log(`Producer exited with code: ${code}`);
    if (signal) console.log(`Producer exited with code: ${signal}`);
});