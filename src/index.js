const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require("child_process");
const path = require('node:path');

if (require('electron-squirrel-startup')) app.quit;

// NOTE: Turn OFF when running "npm run make"
//  - To run with DEBUG=false, make sure the landmarker module is compiled and is located in "Yoge/landmarker/"
const DEBUG = true;
const spawnoption = DEBUG ? "python" : "landmarker/landmarker.exe";
const spawnargs = DEBUG ? ['src/modules/landmarker-service/main.py', '-user=0', '-sequence=1', '-session=2'] : ['-user=0', '-sequence=1', '-session=2'];

// Create the browser window and start the consumer script.
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
  
  var producer = undefined;

  // Open the DevTools.
  // mainWindow.webContents.openDevTools();

  /**
   * Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
   */
  ipcMain.on("run-consumer", () => {
    var strBuffer;
    try {
      producer = spawn(spawnoption, spawnargs);
      producer.stdout.on('data', (data)=>{
        try {
          strBuffer = data.toString().split("'")[1];
        } catch (err) { console.log("Error Caught:", err); }

        try { 
          mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${strBuffer}`);
        } catch (err) { console.log("Error Caught:", err); }
      });
    
      producer.stderr.on('data', (data)=>{console.log(`${data}`)});

      producer.on('close', (code, signal)=>{
        if (signal) console.log(`Producer exited with code: ${signal}`);
        if (code) console.log(`Producer exited with code: ${code}`);
      });

    } catch (error) {
      console.log(`Encountered an error while connecting: \n${error}`);
    }
  });

  ipcMain.on("stop-consumer", ()=>{
    if (producer) {
      producer.kill();
      producer = undefined;
    }
  });

  ipcMain.on("window-close", ()=>{
    if (producer) {
      producer.kill();
      producer = undefined;
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