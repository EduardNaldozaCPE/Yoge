const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require("child_process");
const path = require('node:path');

if (require('electron-squirrel-startup')) app.quit;

// NOTE: Turn OFF when running "npm run make"
//  - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/landmarker/"
const DEBUG = true;
const spawnoption = DEBUG ? "python" : "landmarker/landmarker.exe";
const spawnargs = DEBUG ? ['src/modules/landmarker-service/main.py', '-user=0', '-sequence=1', '-session=2'] : ['-user=0', '-sequence=1', '-session=2'];

// Create the browser window and start the landmarker script.
const createWindow = () => {
  const mainWindow = new BrowserWindow({
    icon: "media/favicon",
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
  
  var landmarker = undefined;

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  /**
   * Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
   */
  ipcMain.on("run-landmarker", (_, device, noCV) => {
    var strBuffer;
    let spawnArgsCopy = spawnargs;
    let connection_success = false;

    spawnArgsCopy.push(`-device=${device}`);
    if (noCV) spawnArgsCopy.push(`-noCV`);

    try {
      landmarker = spawn(spawnoption, spawnArgsCopy);
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
        case 0:
          mainWindow.webContents.send('landmarker-status', "NORMAL");
          break;
        case 1:
          mainWindow.webContents.send('landmarker-status', "NOVIDEO");
          break;
        default:
          break;
      }
    });
    
    // Print stderr logs
    landmarker.stderr.on('data', (data)=>{console.log(`${data}`)});
  });

  ipcMain.on("stop-landmarker", ()=>{
    if (landmarker) {
      landmarker.kill();
      landmarker = undefined;
    }
  });

  ipcMain.on("restart-landmarker", (_, device, noCV) => {
    // Kill landmarker if it still exists, then signal to re-call run-landmarker.
    if (landmarker !== undefined) {
      while (!landmarker.killed) { 
        landmarker.kill();
        console.log("Waiting for Landmarker to die."); 
      }
      landmarker = undefined
    }
    console.log("Landmarker is dead. Running a new one...");
    mainWindow.webContents.send('recall-landmarker', device, noCV)
  });

  ipcMain.on("window-close", ()=>{
    if (landmarker) {
      landmarker.kill();
      landmarker = undefined;
    }
    mainWindow.close()
  });
  
  ipcMain.on("window-maximize", ()=>{
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    else mainWindow.maximize();
  });

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