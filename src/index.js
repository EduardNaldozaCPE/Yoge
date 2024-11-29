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
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const path = __importStar(require("node:path"));
const sqlite = __importStar(require("sqlite3"));
const electron_1 = require("electron");
const process_1 = require("process");
const config_1 = require("./config");
const landmarker_api_1 = require("./api/landmarker-api");
const utils_1 = require("./utils/utils");
const SequenceModel_1 = require("./models/SequenceModel");
const HistoryModel_1 = require("./models/HistoryModel");
const SessionModel_1 = require("./models/SessionModel");
const ScoreModel_1 = require("./models/ScoreModel");
const PoseModel_1 = require("./models/PoseModel");
const sqlite3 = sqlite.verbose();
if (require('electron-squirrel-startup'))
    electron_1.app.quit;
// NOTE: Turn OFF when running "npm run make"
const DEBUG = false; // - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/resources/landmarker/landmarker.exe"
const spawncommand = DEBUG ? "python" : path.join((0, process_1.cwd)(), config_1.landmarkerConfig.LANDMARKER_PATH);
const spawnargs = DEBUG ? ['src/services/landmarker-service/main.py'] : [];
const db = new sqlite3.Database(config_1.landmarkerConfig.DB_PATH);
// Models
const sequence = new SequenceModel_1.SequenceModel(db);
const history = new HistoryModel_1.HistoryModel(db);
const session = new SessionModel_1.SessionModel(db);
const score = new ScoreModel_1.ScoreModel(db);
const pose = new PoseModel_1.PoseModel(db);
const landmarkerAPI = new landmarker_api_1.LandmarkerAPI(spawncommand, spawnargs);
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
    mainWindow.loadURL("http://localhost:5173/"); // Use this in dev 
    // mainWindow.loadFile(path.join(__dirname,"app/dist/index.html")); // Use this when building
    mainWindow.setMenu(null);
    // Open the DevTools.
    mainWindow.webContents.openDevTools();
    // Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
    electron_1.ipcMain.handle("run-landmarker", (_, userId, sequenceId, device) => {
        // Restart landmarker if it is already running.
        if (landmarkerAPI.isInstanceExists()) {
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
            landmarkerAPI.start();
        }
        catch (error) {
            console.log(`Encountered an error while connecting: \n${error}`);
        }
        finally {
            mainWindow.webContents.send("on-session", sessionId);
        }
        // Parse Data to image src string & Signal landmarker-status "SUCCESS" on the first data sent
        landmarkerAPI.onData((data) => {
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
        landmarkerAPI.onClose(() => {
            mainWindow.webContents.send('landmarker-status', "NORMAL");
        }, () => {
            mainWindow.webContents.send('landmarker-status', "NOVIDEO");
        });
        // Print stderr logs
        landmarkerAPI.onCommand((_) => {
            mainWindow.webContents.send('next-pose');
        }, (data) => {
            console.log(data.toString());
        }, () => {
            mainWindow.webContents.send('session-done');
        });
    });
    // Kills the landmarker child process
    electron_1.ipcMain.handle("stop-landmarker", () => {
        landmarkerAPI.kill();
        if (landmarkerAPI.isInstanceExists()) {
            throw new Error("Error killing landmarkerAPI");
        }
    });
    electron_1.ipcMain.handle("record-history", (_, sessionId, score) => {
        history.postNewHistory(sessionId, score);
    });
    // kills the landmarker child process, then signals 'recall-landmarker' which calls 'run-landmarker'
    electron_1.ipcMain.handle("restart-landmarker", (_, userId, sequenceId, device) => {
        landmarkerAPI.kill();
        if (landmarkerAPI.isInstanceExists()) {
            throw new Error("Error killing landmarkerAPI");
        }
        console.log(`Landmarker is dead. Running a new one...`);
        mainWindow.webContents.send('recall-landmarker', userId, sequenceId, device);
    });
    electron_1.ipcMain.handle("cmd-start", () => {
        landmarkerAPI.send_command("play");
    });
    electron_1.ipcMain.handle("cmd-pause", () => {
        landmarkerAPI.send_command("pause");
    });
    // kills the landmarker child process and closes the window.
    electron_1.ipcMain.handle("window-close", () => {
        landmarkerAPI.kill();
        if (landmarkerAPI.isInstanceExists()) {
            throw new Error("Error killing landmarkerAPI");
        }
        mainWindow.close();
    });
    // Toggles between maximize() and unmaximize().
    electron_1.ipcMain.handle("window-maximize", () => {
        if (mainWindow.isMaximized())
            mainWindow.unmaximize();
        else
            mainWindow.maximize();
    });
    // Minimizes the window.
    electron_1.ipcMain.handle("window-minimize", () => mainWindow.minimize());
    // Query
    electron_1.ipcMain.handle("get-score", () => __awaiter(void 0, void 0, void 0, function* () {
        try {
            return yield score.get_latest_score();
        }
        catch (e) {
            console.error(e);
        }
    }));
    electron_1.ipcMain.handle("get-poses", (ev, sequenceId) => __awaiter(void 0, void 0, void 0, function* () {
        try {
            return yield pose.get_steps_from_sequenceId(sequenceId);
        }
        catch (e) {
            console.error(e);
        }
    }));
    electron_1.ipcMain.handle("get-history", (ev, sequenceId) => __awaiter(void 0, void 0, void 0, function* () {
        try {
            return yield history.get_history_from_sequenceId(sequenceId);
        }
        catch (e) {
            console.error(e);
        }
    }));
    electron_1.ipcMain.handle("get-all-history", (_) => __awaiter(void 0, void 0, void 0, function* () {
        try {
            return yield history.get_all_history();
        }
        catch (e) {
            console.error(e);
        }
    }));
    electron_1.ipcMain.handle("get-sequence-data", (ev, sequenceId) => __awaiter(void 0, void 0, void 0, function* () {
        try {
            return yield sequence.get_sequence_from_sequenceId(sequenceId);
        }
        catch (e) {
            console.error(e);
        }
    }));
    electron_1.ipcMain.handle("get-pose-records", (ev, sequenceId) => __awaiter(void 0, void 0, void 0, function* () {
        let poses = [];
        let scores = [];
        let poseRecords = [];
        try {
            poses = yield pose.get_steps_from_sequenceId(sequenceId);
            scores = yield score.get_scores_from_sequenceId(sequenceId);
            poseRecords = (0, utils_1.response2PoseRecord)(scores, poses);
        }
        catch (e) {
            console.error(e);
        }
        finally {
            return poseRecords;
        }
    }));
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
