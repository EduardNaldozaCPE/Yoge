import * as path from 'node:path';
import { app, BrowserWindow, ipcMain } from 'electron';
import { cwd } from 'process';
import { landmarkerConfig } from './config';
import { SessionModel } from './models/SessionModel';
import { LandmarkerAPI } from './api/landmarker-api';
import { PoseRecord, response2PoseRecord } from './utils/utils';


if ( require('electron-squirrel-startup') ) app.quit;

// NOTE: Turn OFF when running "npm run make"
// 
const DEBUG = true;
// 
// - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/resources/landmarker/landmarker.exe"
const spawncommand: string = DEBUG? "python" : path.join(cwd(), landmarkerConfig.LANDMARKER_PATH);
const spawnargs: Array<string> = DEBUG? ['src/services/landmarker-service/main.py'] : [];
const session = new SessionModel();

const landmarkerAPI = new LandmarkerAPI(spawncommand, spawnargs)


// Create the browser window and start the landmarker script.
const createWindow = () => {
  const mainWindow = new BrowserWindow({
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

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.setMenu(null);

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  // Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
  ipcMain.on("run-landmarker", (_, userId, sequenceId, device) => {

    // Restart landmarker if it is already running.
    if (landmarkerAPI.isInstanceExists()) {
      mainWindow.webContents.send('restart-landmarker', device);
      return;
    }

    var strBuffer: string;
    let spawnArgsCopy = spawnargs;
    let connection_success = false;

    let sessionId = Math.floor( Date.now() );
    spawnArgsCopy.push(`-user=${userId}`);
    spawnArgsCopy.push(`-sequence=${sequenceId}`);
    spawnArgsCopy.push(`-session=${sessionId}`);
    spawnArgsCopy.push(`-device=${device}`);

    try {
      landmarkerAPI.start();
    } catch (error) { 
      console.log(`Encountered an error while connecting: \n${error}`); 
    } finally {
      mainWindow.webContents.send("on-session", sessionId);
    }

    // Parse Data to image src string & Signal landmarker-status "SUCCESS" on the first data sent
    landmarkerAPI.onData((data)=>{
      try {
        strBuffer = data.toString().split("'")[1];
      } catch (err) { console.log("Error Caught:", err); }

      mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${strBuffer}`);

      if (connection_success) return;
      connection_success = true;
      mainWindow.webContents.send('landmarker-status', "SUCCESS")
    });

    // Signal landmarker-status on close.
    landmarkerAPI.onClose(
      ()=>{
        mainWindow.webContents.send('landmarker-status', "NORMAL");
      },
      () => {
        mainWindow.webContents.send('landmarker-status', "NOVIDEO");
      }
    );
    
    // Print stderr logs
    landmarkerAPI.onCommand(
      (_)=>{
        mainWindow.webContents.send('next-pose');
      },
      (data)=>{
        console.log(data.toString());  
      },
      ()=>{
        mainWindow.webContents.send('session-done');
      }
    );
  });

  // Kills the landmarker child process
  ipcMain.on("stop-landmarker", ()=>{
    landmarkerAPI.kill()
    if (landmarkerAPI.isInstanceExists()) {
      throw new Error("Error killing landmarkerAPI");
    }
  });

  ipcMain.on("record-history", (_, sessionId, score)=>{
    session.postNewHistory(sessionId, score);
  });

  // kills the landmarker child process, then signals 'recall-landmarker' which calls 'run-landmarker'
  ipcMain.on("restart-landmarker", (_, userId, sequenceId, device) => {
    landmarkerAPI.kill();
    if (landmarkerAPI.isInstanceExists()) {
      throw new Error("Error killing landmarkerAPI");
    }
    console.log(`Landmarker is dead. Running a new one...`);
    mainWindow.webContents.send('recall-landmarker', userId, sequenceId, device)
  });

  ipcMain.on("cmd-start", ()=>{
    landmarkerAPI.send_command("play");
  });

  ipcMain.on("cmd-pause", ()=>{
    landmarkerAPI.send_command("pause");
  });

  // kills the landmarker child process and closes the window.
  ipcMain.on("window-close", ()=>{
    landmarkerAPI.kill();
    if (landmarkerAPI.isInstanceExists()) {
      throw new Error("Error killing landmarkerAPI");
    }
    mainWindow.close()
  });

  // Toggles between maximize() and unmaximize().
  ipcMain.on("window-maximize", ()=>{
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    else mainWindow.maximize();
  });

  // Minimizes the window.
  ipcMain.on("window-minimize", ()=>mainWindow.minimize());

  // Query
  ipcMain.on("get-score", (ev)=>{
    session.get_latest_score((status, data)=>{
      if (status == 'success') {
        ev.sender.send('on-score', data);
      }
    });
  });

  ipcMain.on("get-poses", (ev, sequenceId)=>{
    console.log(`RUNNING GET POSES (${sequenceId})`);
    session.get_steps_from_sequenceId(sequenceId, (status, data)=>{
      if (status == 'success') {
        ev.sender.send('on-poses', data);
      }
    });
  });

  ipcMain.on("get-history", (ev, sequenceId)=>{
    console.log(`RUNNING GET HISTORY`);
    session.get_history_from_sequenceId(sequenceId, (status, data)=>{
      if (status == 'success') {
        ev.sender.send('on-history', data);
      }
    });
  });

  ipcMain.on("get-all-history", (ev)=>{
    console.log(`RUNNING GET ALL HISTORY`);
    session.get_all_history((status, data)=>{
      if (status == 'success') {
        ev.sender.send('on-all-history', data);
      }
    });
  });

  ipcMain.on("get-pose-records", (ev, sequenceId)=>{
    console.log(`RUNNING GET POSE RECORDS`);
    session.get_steps_from_sequenceId(sequenceId, (status, poses)=>{
      if (status != 'success') return;
      session.get_scores_from_sequenceId(sequenceId, (status,data)=>{
        let poseRecords:Array<PoseRecord> = response2PoseRecord(status,data,poses);
        ev.sender.send('on-pose-records', poseRecords);
      });
    });
  });

  ipcMain.on("get-sequence-data", (ev, sequenceId)=>{
    session.get_sequence_from_sequenceId(sequenceId, (status, data)=>{
      if (status == 'success') {
        ev.sender.send('on-sequence-data', data);
      }
    });
  });

};


app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});