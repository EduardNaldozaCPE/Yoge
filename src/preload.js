const { contextBridge, ipcRenderer } = require('electron/renderer')

contextBridge.exposeInMainWorld('landmarkerAPI', {

    // Functions
    run: (userId, sequenceId, device=0, noCV=false) => {ipcRenderer.send('run-landmarker', userId, sequenceId, device, noCV)},
    onSession: (callback) => ipcRenderer.on('on-session', (ev, sessionId)=>{callback(sessionId)}),
    restart: (device=0, noCV=false) => ipcRenderer.send('restart-landmarker', device, noCV),
    stop: () => ipcRenderer.send('stop-landmarker'),

    play: () => ipcRenderer.send('cmd-start'),
    pause: () => ipcRenderer.send('cmd-pause'),

    getScore: () => ipcRenderer.send('get-score'),
    onScore: (callback) => ipcRenderer.on('on-score', (ev, data)=>{callback(data)}),

    getPoses: (sequenceId) => ipcRenderer.send('get-poses', sequenceId),
    onPoses: (callback) => ipcRenderer.on('on-poses', (ev, data)=>{callback(data)}),

    getSequenceData: (sequenceId) => ipcRenderer.send('get-sequence-data', sequenceId),
    onSequenceData: (callback) => ipcRenderer.on('on-sequence-data', (ev, data)=>{callback(data)}),

    onNextPose: (callback) => ipcRenderer.on('next-pose', ()=>{callback()}),

    // Callbacks 
    onFrame: (callback) => {ipcRenderer.on('current-frame', (_, imgStr)=> callback(imgStr))},
    onStatus: (successCallback, failCallback) => {ipcRenderer.on('landmarker-status', (_, status)=>{
        switch (status) {
            case "SUCCESS": successCallback(); break;
            case "NOVIDEO": failCallback(); break;
            case "SIGTERM": break;
            default: break;
        }
    })},
    enableRestart: (restartListener=()=>{}) => {
        ipcRenderer.on('recall-landmarker', (_, device, noCV)=>{
            restartListener()
            ipcRenderer.send('run-landmarker', device, noCV);
        });
        ipcRenderer.on('restart-landmarker', (_, device, noCV)=>{
            console.log("Restarted Landmarker from Main.");
            ipcRenderer.send('restart-landmarker', device, noCV);
        })
    },
})


contextBridge.exposeInMainWorld('electronWindow', {
    windowClose: () => ipcRenderer.send('window-close'),
    windowMinimize: () => ipcRenderer.send('window-minimize'),
    windowMaximize: () => ipcRenderer.send('window-maximize'),
    transitionTo: (loc) => {
        const appContent = document.getElementById("app-content").style;
        appContent.animation = "opentransition 0.2s linear backwards";
        setTimeout(()=>{ appContent.opacity = 0; }, 10);
        setTimeout(()=>{ location.href = loc; }, 200);
    }
})