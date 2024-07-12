const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require("child_process");
const path = require('node:path');

if (require('electron-squirrel-startup')) app.quit;

// Create the browser window and start the consumer script.
const createWindow = () => {
  const mainWindow = new BrowserWindow({
    icon: "media/favicon",
    width: 1280,
    height: 720,
    titleBarStyle: 'hidden',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.setMenu(null);

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  /**
   * Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
   */
  const runConsumer = () => {
    try {
      const producer = spawn('python', ['src/modules/landmarker-service/main.py', '-user=0', '-sequence=1', '-session=2']);

      var outCount = 0;

      producer.stdout.on('data', (data)=>{
        outCount++;
        strData = data.toString().substring(0, 15);
        console.log(`[${outCount}] out: ${strData}`);
        // mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${buf_bodyAndPadding[0]}`);
      });
    
      producer.stderr.on('data', (data)=>{
        console.log(`${data}`);
      });

      producer.on('close', (code, signal)=>{
        if (code) console.log(`Producer exited with code: ${code}`);
        if (signal) console.log(`Producer exited with code: ${signal}`);
      });
    } catch (error) {
      console.log(`Encountered an error while connecting: \n${error}`);
    }
  }; 

  ipcMain.on("run-consumer", runConsumer);
  ipcMain.on("window-close", ()=>mainWindow.close());
  ipcMain.on("window-minimize", ()=>mainWindow.minimize());
  ipcMain.on("window-maximize", ()=>{
    if (mainWindow.isMaximized()) mainWindow.unmaximize();
    else mainWindow.maximize();
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