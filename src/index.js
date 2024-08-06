"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
const path = __importStar(require("node:path"));
const electron_1 = require("electron");
const node_child_process_1 = require("node:child_process");
const process_1 = require("process");
const config_1 = require("./config");
const SessionModel_1 = require("./models/SessionModel");
if (require('electron-squirrel-startup'))
    electron_1.app.quit;
// NOTE: Turn OFF when running "npm run make"
// 
const DEBUG = true;
// 
// - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/resources/landmarker/landmarker.exe"
const spawncommand = DEBUG ? "python" : path.join((0, process_1.cwd)(), config_1.landmarkerConfig.LANDMARKER_PATH);
const spawnargs = DEBUG ? ['src/services/landmarker-service/main.py'] : [];
const session = new SessionModel_1.SessionModel();
// Create the browser window and start the landmarker script.
const createWindow = () => {
    const mainWindow = new electron_1.BrowserWindow({
        icon: "appicon",
        width: 1280,
        height: 720,
        minHeight: 700,
        minWidth: 1200,
        titleBarStyle: 'hidden',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        },
    });
    let landmarker;
    mainWindow.loadFile(path.join(__dirname, 'index.html'));
    mainWindow.setMenu(null);
    // Open the DevTools.
    mainWindow.webContents.openDevTools();
    // Command Queue IPC
    const cmdQueue_path = path.join((0, process_1.cwd)(), "resources/ipc/to_landmarker.csv");
    function send_ipc(command) {
        // fs.writeFileSync(cmdQueue_path, `${Date.now()},${command}`);
        try {
            if (landmarker instanceof node_child_process_1.ChildProcess) {
                landmarker.stdin.write(`${command}\n`);
                console.log("SENT COMMAND: " + command);
            }
        }
        catch (e) {
            console.log("Error while sending to landmarker: ", e);
        }
    }
    // Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
    electron_1.ipcMain.on("run-landmarker", (_, userId, sequenceId, device) => {
        // Restart landmarker if it is already running.
        if (landmarker != undefined) {
            mainWindow.webContents.send('restart-landmarker', device);
            return;
        }
        var strBuffer;
        let spawnArgsCopy = spawnargs;
        let connection_success = false;
        let sessionId = Math.floor(Date.now());
        spawnArgsCopy.push(`-user=${userId}`);
        spawnArgsCopy.push(`-sequence=${sequenceId}`);
        spawnArgsCopy.push(`-session=${sessionId}`);
        spawnArgsCopy.push(`-device=${device}`);
        try {
            landmarker = (0, node_child_process_1.spawn)(spawncommand, spawnArgsCopy);
        }
        catch (error) {
            console.log(`Encountered an error while connecting: \n${error}`);
        }
        finally {
            mainWindow.webContents.send("on-session", sessionId);
        }
        // Parse Data to image src string & Signal landmarker-status "SUCCESS" on the first data sent
        landmarker.stdout.on('data', (data) => {
            try {
                strBuffer = data.toString().split("'")[1];
            }
            catch (err) {
                console.log("Error Caught:", err);
            }
            mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${strBuffer}`);
            if (connection_success)
                return;
            connection_success = true;
            mainWindow.webContents.send('landmarker-status', "SUCCESS");
        });
        // Signal landmarker-status on close.
        landmarker.on('close', (code, signal) => {
            if (signal == "SIGTERM") {
                try {
                    mainWindow.webContents.send('landmarker-status', "SIGTERM");
                }
                catch (e) {
                    if (e instanceof TypeError)
                        return;
                }
            }
            switch (code) {
                case null: break;
                case 0:
                    mainWindow.webContents.send('landmarker-status', "NORMAL");
                    break;
                case 1:
                    mainWindow.webContents.send('landmarker-status', "NOVIDEO");
                    break;
                default:
                    console.log("Landmarker closed with code: ", code);
                    break;
            }
        });
        // Print stderr logs
        landmarker.stderr.on('data', (data) => {
            let prefix = data.toString().substring(0, 5);
            if (prefix == "NPOSE") {
                mainWindow.webContents.send('next-pose');
            }
            else {
                console.log(`${data}`);
            }
        });
    });
    // Kills the landmarker child process
    electron_1.ipcMain.on("stop-landmarker", () => {
        if (landmarker) {
            landmarker.kill();
            landmarker = null;
        }
    });
    // kills the landmarker child process, then signals 'recall-landmarker' which calls 'run-landmarker'
    electron_1.ipcMain.on("restart-landmarker", (_, userId, sequenceId, device) => {
        if (landmarker != null) {
            landmarker.kill();
            landmarker = null;
        }
        console.log(`Landmarker is dead (${landmarker}). Running a new one...`);
        mainWindow.webContents.send('recall-landmarker', userId, sequenceId, device);
    });
    electron_1.ipcMain.on("cmd-start", () => {
        send_ipc("play");
    });
    electron_1.ipcMain.on("cmd-pause", () => {
        send_ipc("pause");
    });
    // kills the landmarker child process and closes the window.
    electron_1.ipcMain.on("window-close", () => {
        if (landmarker) {
            landmarker.kill();
            landmarker = null;
        }
        mainWindow.close();
    });
    // Toggles between maximize() and unmaximize().
    electron_1.ipcMain.on("window-maximize", () => {
        if (mainWindow.isMaximized())
            mainWindow.unmaximize();
        else
            mainWindow.maximize();
    });
    // Minimizes the window.
    electron_1.ipcMain.on("window-minimize", () => mainWindow.minimize());
    // Query
    electron_1.ipcMain.on("get-score", (ev) => {
        session.get_latest_score((status, data) => {
            if (status == 'success') {
                ev.sender.send('on-score', data);
            }
        });
    });
    electron_1.ipcMain.on("get-poses", (ev, sequenceId) => {
        console.log(`RUNNING GET POSES (${sequenceId})`);
        session.get_steps_from_sequenceId(sequenceId, (status, data) => {
            if (status == 'success') {
                ev.sender.send('on-poses', data);
            }
        });
    });
    electron_1.ipcMain.on("get-sequence-data", (ev, sequenceId) => {
        session.get_sequence_from_sequenceId(sequenceId, (status, data) => {
            if (status == 'success') {
                ev.sender.send('on-sequence-data', data);
            }
        });
    });
};
electron_1.app.whenReady().then(() => {
    createWindow();
    electron_1.app.on('activate', () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});
electron_1.app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
