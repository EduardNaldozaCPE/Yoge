const { spawn } = require('child_process');

// Spawn the Python script
// const pythonProcess = spawn('python', ['src/tests/script.py']);
const pythonProcess = spawn('python', ['src/services/landmarker-service/main.py', '-user=0', '-sequence=1', '-session=2000', '-device=0', '-lenOnly']);

// Handle data from Python script
pythonProcess.stdout.on('data', (data) => {
  console.log(`Received from Python: ${data}`);
});

// Handle error output from Python script
pythonProcess.stderr.on('data', (data) => {
  console.error(`Error from Python: ${data}`);
});

// Handle Python script exit
pythonProcess.on('close', (code) => {
  console.log(`Python script exited with code ${code}`);
});

// Send data to Python script
function sendDataToPython(data) {
  pythonProcess.stdin.write(`${data}\n`);
}

// Example of sending data to Python script
setInterval(() => {
  const data = `ooga`;
  console.log(`Sending to Python: ${data}`);
  sendDataToPython(data);
}, 2000);