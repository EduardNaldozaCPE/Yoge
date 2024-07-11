const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const net = require('node:net');
const PIPEDIR = "\\\\.\\pipe\\framePipe";

if (require('electron-squirrel-startup')) app.quit;

// Create the browser window and start the consumer script.
const createWindow = () => {
  const mainWindow = new BrowserWindow({
    icon: "/media/favicon.ico",
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
  // mainWindow.webContents.openDevTools();

  /**
   * Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
   */
  const runConsumer = () => {
    console.log(`Connecting to named pipe: ${PIPEDIR}`);
    try {
      client = net.createConnection( `${PIPEDIR}`, ()=>console.log("Successfully Connected."));
      
      // Upon retrieval of new data, format the bytestring and signal current-frame event in preload
      client.on('data', (data) => {
        let buf_bodyAndPadding = data.toString('base64').split("BUFFEREND");
        try {
          mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${buf_bodyAndPadding[0]}`);
        } catch (err) {
          if (typeof(err) == TypeError) console.log("Error Caught: ", err);
        }
      });

      client.on('end', () => {
        console.log("Disconnecting from the named pipe.")
        client.close();
      });

    } catch (error) {
      console.log(`Encountered an error while connecting: \n${error}`);
    }
  }; ipcMain.on("run-consumer", runConsumer);

  ipcMain.on("window-close", ()=>mainWindow.close());
  ipcMain.on("window-minimize", ()=>mainWindow.minimize());
  ipcMain.on("window-maximize", ()=>{
    if (mainWindow.isMaximized())
      mainWindow.unmaximize();
    else
      mainWindow.maximize();
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