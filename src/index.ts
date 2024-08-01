import * as path from 'node:path';
import * as fs from 'fs';
import { landmarkerCommand } from './dataTypes';
import { app, BrowserWindow, ipcMain } from 'electron';
import { spawn, ChildProcess } from "node:child_process";
import { cwd } from 'process';
import { landmarkerConfig } from './config';
import { SessionModel } from './models/SessionModel';


if ( require('electron-squirrel-startup') ) app.quit;

// NOTE: Turn OFF when running "npm run make"
// 
const DEBUG = true;
// 
// - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/resources/landmarker/landmarker.exe"
const spawncommand: string = DEBUG? "python" : path.join(cwd(), landmarkerConfig.LANDMARKER_PATH);
const spawnargs: Array<string> = DEBUG? ['src/services/landmarker-service/main.py'] : [];
const session = new SessionModel();


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
  
  var landmarker: ChildProcess | null;

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.setMenu(null);

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  // Command Queue IPC
  const cmdQueue_path = path.join(cwd(), "resources/ipc/to_landmarker.csv");

  function _add_ipc_command(command:landmarkerCommand) {
    fs.writeFileSync(cmdQueue_path, `${Date.now()},${command}`);
  }

  // Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
  ipcMain.on("run-landmarker", (_, userId, sequenceId, device) => {
    var strBuffer: string;
    let spawnArgsCopy = spawnargs;
    let connection_success = false;

    // Restart landmarker if it is already running.
    if (landmarker != undefined) {
      mainWindow.webContents.send('restart-landmarker', device);
      return;
    }
    let sessionId = Math.floor( Date.now() );
    spawnArgsCopy.push(`-user=${userId}`);
    spawnArgsCopy.push(`-sequence=${sequenceId}`);
    spawnArgsCopy.push(`-session=${sessionId}`);
    spawnArgsCopy.push(`-device=${device}`);

    try {
      landmarker = spawn(spawncommand, spawnArgsCopy);
    } catch (error) { 
      console.log(`Encountered an error while connecting: \n${error}`); 
    } finally {
      mainWindow.webContents.send("on-session", sessionId);
    }

    // Parse Data to image src string & Signal landmarker-status "SUCCESS" on the first data sent
    landmarker!.stdout!.on('data', (data)=>{
      try {
        strBuffer = data.toString().split("'")[1];
      } catch (err) { console.log("Error Caught:", err); }

      mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${strBuffer}`);

      if (connection_success) return;
      connection_success = true;
      mainWindow.webContents.send('landmarker-status', "SUCCESS")
    });

    // Signal landmarker-status on close.
    landmarker!.on('close', (code, signal)=>{
      if (signal == "SIGTERM") {
        try {
          mainWindow.webContents.send('landmarker-status', "SIGTERM");
        } catch (e) { if (e instanceof TypeError) return }
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
    landmarker!.stderr!.on('data', (data)=>{
      let prefix = data.toString().substring(0,5);
      if (prefix == "NPOSE") {
        mainWindow.webContents.send('next-pose');
      } else {
        console.log(`${data}`);
      }
    });
  });

  // Kills the landmarker child process
  ipcMain.on("stop-landmarker", ()=>{
    if (landmarker) {
      landmarker.kill();
      landmarker = null;
    }
  });

  // kills the landmarker child process, then signals 'recall-landmarker' which calls 'run-landmarker'
  ipcMain.on("restart-landmarker", (_, userId, sequenceId, device) => {
    if (landmarker != null) {
      landmarker.kill();
      landmarker = null;
    }
    console.log(`Landmarker is dead (${landmarker}). Running a new one...`);
    mainWindow.webContents.send('recall-landmarker', userId, sequenceId, device)
  });

  ipcMain.on("cmd-start", ()=>{
    _add_ipc_command("PLAY");
  });

  ipcMain.on("cmd-pause", ()=>{
    _add_ipc_command("PAUSE");
  });

  // kills the landmarker child process and closes the window.
  ipcMain.on("window-close", ()=>{
    if (landmarker) {
      landmarker.kill();
      landmarker = null;
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
    session.get_latest_score((data)=>{
      ev.sender.send('on-score', data);
    });
  });

  ipcMain.on("get-poses", (ev, sequenceId)=>{
    console.log(`RUNNING GET POSES (${sequenceId})`);
    session.get_steps_from_sequenceId(sequenceId, (data)=>{
      ev.sender.send('on-poses', data);
    });
  })

  ipcMain.on("get-sequence-data", (ev, sequenceId)=>{
    session.get_sequence_from_sequenceId(sequenceId, (data)=>{
      ev.sender.send('on-sequence-data', data);
    });
  })

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