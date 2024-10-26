import { IElectronWindow, ILandmarkerAPI } from "./interface";
const { contextBridge, ipcRenderer } = require('electron/renderer')

const landmarkerAPI : ILandmarkerAPI = {
    // Feed Control
    run: (userId: number, sequenceId: number, device=0) => ipcRenderer.invoke('run-landmarker', userId, sequenceId, device),
    restart: (userId: number, sequenceId: number, device=0) => ipcRenderer.invoke('restart-landmarker', userId, sequenceId, device),
    stop: () => ipcRenderer.invoke('stop-landmarker'),
    play: () => ipcRenderer.invoke('cmd-start'),
    pause: () => ipcRenderer.invoke('cmd-pause'),
    
    // Database Operations
    getScore: () => ipcRenderer.invoke('get-score'),
    getPoses: (sequenceId: number) => ipcRenderer.invoke('get-poses', sequenceId),
    getAllHistory: () => ipcRenderer.invoke('get-all-history'),
    getHistory: (sequenceId:number) => ipcRenderer.invoke('get-history', sequenceId),
    getPoseRecords: (sequenceId:number) => ipcRenderer.invoke('get-pose-records', sequenceId),
    getSequenceData: (sequenceId: number) => ipcRenderer.invoke('get-sequence-data', sequenceId),
    recordHistory: (sessionId: number, score: number) => ipcRenderer.invoke('record-history', sessionId, score),
    
    // Callbacks 
    onSession: (callback: Function) => ipcRenderer.on('on-session', (ev, sessionId)=>{callback(sessionId)}),
    onSessionDone: (callback: Function) => {ipcRenderer.on('session-done', ()=> callback())},
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
            ipcRenderer.invoke('run-landmarker', userId, sequenceId, device);
        });
    },
}

const electronWindow : IElectronWindow = {
    windowClose: () => ipcRenderer.invoke('window-close'),
    windowMinimize: () => ipcRenderer.invoke('window-minimize'),
    windowMaximize: () => ipcRenderer.invoke('window-maximize'),
    transitionTo: (loc: string) => {
        const appContent = document.getElementById("app-content")!.style;
        appContent.animation = "opentransition 0.2s linear backwards";
        setTimeout(()=>{ appContent.opacity = "0"; }, 10);
        setTimeout(()=>{ location.href = loc; }, 200);
    }
}

contextBridge.exposeInMainWorld('landmarkerAPI', landmarkerAPI)
contextBridge.exposeInMainWorld('electronWindow', electronWindow);