const { contextBridge, ipcRenderer } = require('electron/renderer')

contextBridge.exposeInMainWorld('landmarkerAPI', {

    // Functions
    run: (userId: number, sequenceId: number, device=0) => ipcRenderer.send('run-landmarker', userId, sequenceId, device),
    onSession: (callback: Function) => ipcRenderer.on('on-session', (ev, sessionId)=>{callback(sessionId)}),

    restart: (userId: number, sequenceId: number, device=0) => ipcRenderer.send('restart-landmarker', userId, sequenceId, device),
    stop: () => ipcRenderer.send('stop-landmarker'),

    play: () => ipcRenderer.send('cmd-start'),
    pause: () => ipcRenderer.send('cmd-pause'),

    getScore: () => ipcRenderer.send('get-score'),
    onScore: (callback: Function) => ipcRenderer.on('on-score', (ev, data)=>{callback(data)}),
    
    getPoses: (sequenceId: number) => ipcRenderer.send('get-poses', sequenceId),
    onPoses: (callback: Function) => ipcRenderer.on('on-poses', (ev, data)=>{callback(data)}),

    getAllHistory: () => ipcRenderer.send('get-all-history'),
    onAllHistory: (callback: Function) => ipcRenderer.on('on-all-history', (_, data)=>{callback(data)}),

    getHistory: (sequenceId:number) => ipcRenderer.send('get-history', sequenceId),
    onHistory: (callback: Function) => ipcRenderer.on('on-history', (_, data)=>{callback(data)}),
    getPoseRecords: (sequenceId:number) => ipcRenderer.send('get-pose-records', sequenceId),
    onPoseRecords: (callback: Function) => ipcRenderer.on('on-pose-records', (_, data)=>{callback(data)}),

    getSequenceData: (sequenceId: number) => ipcRenderer.send('get-sequence-data', sequenceId),
    onSequenceData: (callback: Function) => ipcRenderer.on('on-sequence-data', (ev, data)=>{callback(data)}),

    onSessionDone: (callback: Function) => {ipcRenderer.on('session-done', ()=> callback())},
    recordHistory: (sessionId: number, score: number) => {ipcRenderer.send('record-history', sessionId, score)},

    // Callbacks 
    onNextPose: (callback: Function) => ipcRenderer.on('next-pose', ()=>{callback()}),
    onFrame: (callback: Function) => {ipcRenderer.on('current-frame', (_, imgStr)=> callback(imgStr))},
    onStatus: (successCallback:Function, failCallback:Function) => {ipcRenderer.on('landmarker-status', (_, status)=>{
        switch (status) {
            case "SUCCESS": successCallback(); break;
            case "NOVIDEO": failCallback(); break;
            case "SIGTERM": break;
            default: break;
        }
    })},
    enableRestart: (userId: number, sequenceId: number, restartListener=()=>{}) => {
        ipcRenderer.on('recall-landmarker', (_, device)=>{
            restartListener()
            ipcRenderer.send('run-landmarker', userId, sequenceId, device);
        });
    },
})


contextBridge.exposeInMainWorld('electronWindow', {
    windowClose: () => ipcRenderer.send('window-close'),
    windowMinimize: () => ipcRenderer.send('window-minimize'),
    windowMaximize: () => ipcRenderer.send('window-maximize'),
    transitionTo: (loc: string) => {
        const appContent = document.getElementById("app-content")!.style;
        appContent.animation = "opentransition 0.2s linear backwards";
        setTimeout(()=>{ appContent.opacity = "0"; }, 10);
        setTimeout(()=>{ location.href = loc; }, 200);
    }
})