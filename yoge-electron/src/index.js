const { 
  app, 
  BrowserWindow,
  ipcMain
} = require('electron');
const path = require('node:path');
const net = require('node:net');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // and load the index.html of the app.
  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  

  const PIPEDIR = "\\\\.\\pipe\\framePipe";
  var imgSrcString = "data:image/png;base64,\x01";

  ipcMain.on("run-consumer", (event) => {
    console.log(`Connecting to named pipe: ${PIPEDIR}`);
    try {
      
      client = net.createConnection( `${PIPEDIR}`, ()=>console.log("Successfully Connected."));
      event.sender.send('consumer-status',true);
      
      client.on('data', (data) => {
        let buf_bodyAndPadding = data.toString('base64').split("BUFFEREND");
        imgSrcString = `data:image/jpg;base64,${buf_bodyAndPadding[0]}`;
        mainWindow.webContents.send('current-frame', imgSrcString);
      });

      client.on('end', () => {
        console.log("Disconnecting from the named pipe.");
      });

    } catch (error) {

      console.log(`Encountered an error while connecting: \n${error}`);
      event.sender.send('consumer-status',false);

    }
  });

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