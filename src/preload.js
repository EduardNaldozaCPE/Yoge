"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const { contextBridge, ipcRenderer } = require('electron/renderer');
const landmarkerAPI = {
    // Feed Control
    run: (userId, sequenceId, device = 0) => ipcRenderer.invoke('run-landmarker', userId, sequenceId, device),
    restart: (userId, sequenceId, device = 0) => ipcRenderer.invoke('restart-landmarker', userId, sequenceId, device),
    stop: () => ipcRenderer.invoke('stop-landmarker'),
    play: () => ipcRenderer.invoke('cmd-start'),
    pause: () => ipcRenderer.invoke('cmd-pause'),
    // Database Operations
    getScore: () => ipcRenderer.invoke('get-score'),
    getPoses: (sequenceId) => ipcRenderer.invoke('get-poses', sequenceId),
    getAllHistory: () => ipcRenderer.invoke('get-all-history'),
    getHistory: (sequenceId) => ipcRenderer.invoke('get-history', sequenceId),
    getPoseRecords: (sequenceId) => ipcRenderer.invoke('get-pose-records', sequenceId),
    getSequenceData: (sequenceId) => ipcRenderer.invoke('get-sequence-data', sequenceId),
    recordHistory: (sessionId, score) => ipcRenderer.invoke('record-history', sessionId, score),
    // Callbacks 
    onSession: (callback) => ipcRenderer.on('on-session', (ev, sessionId) => { callback(sessionId); }),
    onSessionDone: (callback) => { ipcRenderer.on('session-done', () => callback()); },
    onNextPose: (callback) => ipcRenderer.on('next-pose', () => { callback(); }),
    onFrame: (callback) => { ipcRenderer.on('current-frame', (_, imgStr) => callback(imgStr)); },
    onStatus: (successCallback, failCallback) => {
        ipcRenderer.on('landmarker-status', (_, status) => {
            switch (status) {
                case "SUCCESS":
                    successCallback();
                    break;
                case "NOVIDEO":
                    failCallback();
                    break;
                case "SIGTERM": break;
                default: break;
            }
        });
    },
    enableRestart: (userId, sequenceId, restartListener) => {
        ipcRenderer.on('recall-landmarker', (_, device) => {
            restartListener();
            ipcRenderer.invoke('run-landmarker', userId, sequenceId, device);
        });
    },
};
const electronWindow = {
    windowClose: () => ipcRenderer.invoke('window-close'),
    windowMinimize: () => ipcRenderer.invoke('window-minimize'),
    windowMaximize: () => ipcRenderer.invoke('window-maximize'),
    transitionTo: (loc) => {
        const appContent = document.getElementById("app-content").style;
        appContent.animation = "opentransition 0.2s linear backwards";
        setTimeout(() => { appContent.opacity = "0"; }, 10);
        setTimeout(() => { location.href = loc; }, 200);
    }
};
contextBridge.exposeInMainWorld('landmarkerAPI', landmarkerAPI);
contextBridge.exposeInMainWorld('electronWindow', electronWindow);
