const { contextBridge, ipcRenderer } = require('electron/renderer')

contextBridge.exposeInMainWorld('landmarkerAPI', {

    // Functions
    run: (device=0, noCV=false) => {ipcRenderer.send('run-landmarker', device, noCV)},
    restart: (device=0, noCV=false) => ipcRenderer.send('restart-landmarker', device, noCV),
    stop: () => ipcRenderer.send('stop-landmarker'),

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
        }
    )},
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