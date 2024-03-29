//NOTE - This MUST be a CommonJS file to be able to use `require` for electron (hence the .cjs extension)
const { app, BrowserWindow, shell } = require("electron");
const path = require("path");

app.on("ready", () => {
  const mainWindow = new BrowserWindow({
    webPreferences: {
      preload: path.join(__dirname, 'electron_preload.cjs'),

      //Both of these must be set like this in order to import node modules (like child_process) in the render code
      nodeIntegration: true,
      contextIsolation: false
    }
  })
  mainWindow.loadFile(path.join(__dirname, "public/index.html"));
  mainWindow.setMinimumSize(1300, 900);
  mainWindow.maximize();
  mainWindow.setBackgroundColor("white");

  //Move any navigation to the default browser
  mainWindow.webContents.on('will-navigate', (event, url) => {
    event.preventDefault();
    shell.openExternal(url);
  });

  //Open the dev tools window automatically
  // mainWindow.webContents.openDevTools();
});
