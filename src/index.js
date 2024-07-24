const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require("child_process");
const { cwd } = require('process');
const path = require('node:path');
const fs = require('fs');

if ( require('electron-squirrel-startup') ) app.quit;

// NOTE: Turn OFF when running "npm run make"
// - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/resources/landmarker/landmarker.exe"
const DEBUG = false;
var landmarkerPath = path.join( cwd(), 'resources/landmarker-config.json' );
var landmarkerConfig = JSON.parse( fs.readFileSync(landmarkerPath, 'utf8') );
const spawncommand = DEBUG? "python" : path.join(cwd(), landmarkerConfig.LANDMARKER_PATH);
const spawnargs = DEBUG? ['src/modules/landmarker-service/main.py', '-user=0', '-sequence=1', '-session=2'] : ['-user=0', '-sequence=1', '-session=2'];

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
  // mainWindow.webContents.openDevTools();

  // Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
  ipcMain.on("run-landmarker", (_, device, noCV) => {
    var strBuffer;
    let spawnArgsCopy = spawnargs;
    let connection_success = false;

    // Restart landmarker if it is already running.
    if (landmarker != undefined) {
      mainWindow.webContents.send('restart-landmarker', device, noCV);
      return;
    }

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
    landmarker.stderr.on('data', (data)=>{console.log(`${data}`)});
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