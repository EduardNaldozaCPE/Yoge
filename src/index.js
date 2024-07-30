const { app, BrowserWindow, ipcMain } = require('electron');
// const { parse } = require('csv-parse/sync');
const sqlite3 = require("sqlite3").verbose();
const { spawn } = require("child_process");
const { cwd } = require('process');
const path = require('node:path');
const fs = require('fs');

if ( require('electron-squirrel-startup') ) app.quit;

// NOTE: Turn OFF when running "npm run make"
// - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/resources/landmarker/landmarker.exe"
const DEBUG = true;
var landmarkerPath = path.join( cwd(), 'resources/landmarker-config.json' );
var landmarkerConfig = JSON.parse( fs.readFileSync(landmarkerPath, 'utf8') );
const spawncommand = DEBUG? "python" : path.join(cwd(), landmarkerConfig.LANDMARKER_PATH);
const spawnargs = DEBUG? ['src/modules/landmarker-service/main.py'] : [];

const db = new sqlite3.Database(landmarkerConfig.DB_PATH);

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
  
  var landmarker = undefined;
  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.setMenu(null);


  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  // Command Queue IPC
  const cmdQueue_path = path.join(cwd(), "resources/ipc/to_landmarker.csv");

  // function _onFileChange(ev) {
  //   if (ev == "change"){
  //     const cmdString = fs.readFileSync(cmdQueue_path,options={encoding: "utf8", flag: 'r'});
  //     const cmdLines = cmdString.toString()
  //     var cmds = parse(cmdLines, { delimiter: ",", skip_empty_lines:true});
  //     for (let i=0; i<cmds.length; i++) {
  //       console.log("FROM: " ,cmds[i][0]);
  //       console.log("ID: " ,cmds[i][1]);
  //       console.log("COMMAND: " ,cmds[i][2]);
  //       console.log('\n');
  //       fs.writeFileSync(cmdQueue_path, "")
  //     }
  //   }
  // }

  // fs.watch(cmdQueue_path, (ev, filename)=>{
  //   if (filename) {
  //     _onFileChange(ev);
  //   } else {
  //     console.log('filename not provided');
  //   }
  // });

  function _add_ipc_command(command) {
    fs.writeFileSync(cmdQueue_path, `${Date.now()},${command}`);
  }


  // Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
  ipcMain.on("run-landmarker", (_, userId, sequenceId, device, noCV) => {
    var strBuffer;
    let spawnArgsCopy = spawnargs;
    let connection_success = false;

    // Restart landmarker if it is already running.
    if (landmarker != undefined) {
      mainWindow.webContents.send('restart-landmarker', device, noCV);
      return;
    }

    spawnArgsCopy.push(`-user=${userId}`);
    spawnArgsCopy.push(`-sequence=${sequenceId}`);
    spawnArgsCopy.push(`-device=${device}`);
    if (noCV) spawnArgsCopy.push(`-noCV`);

    try {
      landmarker = spawn(spawncommand, spawnArgsCopy);
    } catch (error) { console.log(`Encountered an error while connecting: \n${error}`); }

    // Parse Data to image src string & Signal landmarker-status "SUCCESS" on the first data sent
    landmarker.stdout.on('data', (data)=>{
      try {
        strBuffer = data.toString().split("'")[1];
      } catch (err) { console.log("Error Caught:", err); }

      mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${strBuffer}`);

      if (connection_success) return
      connection_success = true;
      mainWindow.webContents.send('landmarker-status', "SUCCESS")
    });

    // Signal landmarker-status on close.
    landmarker.on('close', (code, signal)=>{
      if (signal == "SIGTERM") {
        try {
          mainWindow.webContents.send('landmarker-status', "SIGTERM");
        } catch (e) { if (typeof(e) == TypeError) return }
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
    landmarker.stderr.on('data', (data)=>{
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
      landmarker = undefined;
    }
  });

  // kills the landmarker child process, then signals 'recall-landmarker' which calls 'run-landmarker'
  ipcMain.on("restart-landmarker", (_, device, noCV) => {
    if (landmarker !== undefined) {
      landmarker.kill();
      landmarker = undefined
    }
    console.log("Landmarker is dead. Running a new one...");
    mainWindow.webContents.send('recall-landmarker', device, noCV)
  });

  ipcMain.on("cmd-start", ()=>{
    _add_ipc_command("START");
  });

  ipcMain.on("cmd-pause", ()=>{
    _add_ipc_command("PAUSE");
  });

  // kills the landmarker child process and closes the window.
  ipcMain.on("window-close", ()=>{
    if (landmarker) {
      landmarker.kill();
      landmarker = undefined;
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

  ipcMain.on("get-score", (ev)=>{
    _get_latest_score((d)=>{
      ev.sender.send('on-score', d);
    });
  });

  ipcMain.on("get-poses", (ev, sequenceId)=>{
    _get_steps_from_sequenceId(sequenceId, (data)=>{
      ev.sender.send('on-poses', data);
    });
  })

  ipcMain.on("get-sequence-data", (ev, sequenceId)=>{
    _get_sequence_from_sequenceId(sequenceId, (data)=>{
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

// region   ----- DB Functions -----

var _lastScore = {
  "scoreId":0,
  "sessionId":0,
  "step":0,
  "leftElbow":0, 
  "rightElbow":0, 
  "leftKnee":0, 
  "rightKnee":0, 
  "leftShoulder":0, 
  "rightShoulder":0, 
  "leftHip":0, 
  "rightHip":0
};

function _get_latest_score(callback) {
  db.get(
    "SELECT * FROM score WHERE scoreId=(SELECT MAX(scoreId) FROM score);",
    (err, row)=>{
      let d = undefined
      if (err) {
        console.log(err);
        d = _lastScore;
      } else {
        d = row;
        _lastScore = row;
      }
      callback(d);
    }
    );
}

function _get_steps_from_session(sessionId ,callback) {
  db.all(`SELECT * FROM session INNER JOIN pose ON session.sequenceId = pose.sequenceId WHERE session.sessionId = ${sessionId};`, (err, rows)=>{
      if (err)
        throw Error("Invalid Session Id in _get_steps_from_session");
      callback(rows);
    });
}

function _get_steps_from_sequenceId(sequenceId ,callback) {
  db.all(`SELECT * FROM pose WHERE sequenceId = 1; = ${sequenceId};`, (err, rows)=>{
      if (err)
        throw Error("Invalid Session Id in _get_steps_from_session");
      callback(rows);
    });
}

function _get_sequence_from_sequenceId(sequenceId ,callback) {
  db.get(`SELECT * FROM sequence WHERE sequenceId = ${sequenceId};`, (err, rows)=>{
      if (err)
        throw Error("Invalid Session Id in _get_steps_from_session");
      callback(rows);
    });
}