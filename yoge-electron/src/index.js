const { 
  app, 
  BrowserWindow,
  ipcMain
} = require('electron');
const path = require('node:path');
const net = require('node:net');

const PIPEDIR = "\\\\.\\pipe\\framePipe";

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

// Create the browser window and Start the consumer script.
const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  /**
   * Connects to the named pipe containing the frames in bytes. Uses `node:net` to update the frame via events.  
   * @param {IpcMainEvent} event 
   */
  function runConsumer(event) {
    console.log(`Connecting to named pipe: ${PIPEDIR}`);
    try {
      client = net.createConnection( `${PIPEDIR}`, ()=>console.log("Successfully Connected."));
      
      // Upon retrieval of new data, format the bytestring and 
      client.on('data', (data) => {
        let buf_bodyAndPadding = data.toString('base64').split("BUFFEREND");
        try {
          mainWindow.webContents.send('current-frame', `data:image/jpg;base64,${buf_bodyAndPadding[0]}`);
        } catch (err) {
          if (typeof(err) == TypeError) console.log("Error Caught: ", err);
        }
      });

      client.on('end', () => {
        console.log("Disconnecting from the named pipe.");
      });

    } catch (error) {
      console.log(`Encountered an error while connecting: \n${error}`);
    }
  }
  ipcMain.on("run-consumer", (event)=>{runConsumer(event);});

  // Open the DevTools.
  mainWindow.webContents.openDevTools();
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow();

  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  delete client;
  delete sessionEvent;
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.