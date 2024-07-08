// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

const { contextBridge, ipcRenderer } = require('electron/renderer')

contextBridge.exposeInMainWorld('electronAPI', {
    runConsumer: () => ipcRenderer.send('run-consumer'),
    runTest: () => {console.log("RUNNING TEST");},
    checkConnection: (callback) => ipcRenderer.on('consumer-status', (_event, arg) => callback(arg)),
    currentFrame: (callback) => ipcRenderer.on('current-frame', (_event, imgStr)=> callback(imgStr)),
})