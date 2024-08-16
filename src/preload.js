"use strict";
const { contextBridge, ipcRenderer } = require('electron/renderer');
contextBridge.exposeInMainWorld('landmarkerAPI', {
    // Functions
    run: (userId, sequenceId, device = 0) => ipcRenderer.send('run-landmarker', userId, sequenceId, device),
    onSession: (callback) => ipcRenderer.on('on-session', (ev, sessionId) => { callback(sessionId); }),
    restart: (userId, sequenceId, device = 0) => ipcRenderer.send('restart-landmarker', userId, sequenceId, device),
    stop: () => ipcRenderer.send('stop-landmarker'),
    play: () => ipcRenderer.send('cmd-start'),
    pause: () => ipcRenderer.send('cmd-pause'),
    getScore: () => ipcRenderer.send('get-score'),
    onScore: (callback) => ipcRenderer.on('on-score', (ev, data) => { callback(data); }),
    getPoses: (sequenceId) => ipcRenderer.send('get-poses', sequenceId),
    onPoses: (callback) => ipcRenderer.on('on-poses', (ev, data) => { callback(data); }),
    getAllHistory: () => ipcRenderer.send('get-all-history'),
    onAllHistory: (callback) => ipcRenderer.on('on-all-history', (_, data) => { callback(data); }),
    getHistory: (sequenceId) => ipcRenderer.send('get-history', sequenceId),
    onHistory: (callback) => ipcRenderer.on('on-history', (_, data) => { callback(data); }),
    getPoseRecords: (sequenceId) => ipcRenderer.send('get-pose-records', sequenceId),
    onPoseRecords: (callback) => ipcRenderer.on('on-pose-records', (_, data) => { callback(data); }),
    getSequenceData: (sequenceId) => ipcRenderer.send('get-sequence-data', sequenceId),
    onSequenceData: (callback) => ipcRenderer.on('on-sequence-data', (ev, data) => { callback(data); }),
    onSessionDone: (callback) => { ipcRenderer.on('session-done', () => callback()); },
    recordHistory: (sessionId, score) => { ipcRenderer.send('record-history', sessionId, score); },
    // Callbacks 
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
    enableRestart: (userId, sequenceId, restartListener = () => { }) => {
        ipcRenderer.on('recall-landmarker', (_, device) => {
            restartListener();
            ipcRenderer.send('run-landmarker', userId, sequenceId, device);
        });
    },
});
contextBridge.exposeInMainWorld('electronWindow', {
    windowClose: () => ipcRenderer.send('window-close'),
    windowMinimize: () => ipcRenderer.send('window-minimize'),
    windowMaximize: () => ipcRenderer.send('window-maximize'),
    transitionTo: (loc) => {
        const appContent = document.getElementById("app-content").style;
        appContent.animation = "opentransition 0.2s linear backwards";
        setTimeout(() => { appContent.opacity = "0"; }, 10);
        setTimeout(() => { location.href = loc; }, 200);
    }
});
