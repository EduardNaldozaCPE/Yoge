const { contextBridge, ipcRenderer } = require('electron/renderer')

contextBridge.exposeInMainWorld('electronAPI', {
    runConsumer: (device=0, noCV=true) => ipcRenderer.send('run-consumer', device, noCV),
    stopConsumer: () => ipcRenderer.send('stop-consumer'),
    currentFrame: (callback) => ipcRenderer.on('current-frame', (_event, imgStr)=> callback(imgStr)),
    transitionTo: (loc) => {
        const appContent = document.getElementById("app-content").style;
        appContent.animation = "opentransition 0.2s linear backwards";
        setTimeout(()=>{ appContent.opacity = 0; }, 10);
        setTimeout(()=>{ location.href = loc; }, 200);
    }
})


contextBridge.exposeInMainWorld('electronWindow', {
    windowClose: () => ipcRenderer.send('window-close'),
    windowMinimize: () => ipcRenderer.send('window-minimize'),
    windowMaximize: () => ipcRenderer.send('window-maximize')
})