//NOTE - This MUST be a CommonJS file to be able to use `require` for electron (hence the .cjs extension)
const { app, BrowserWindow } = require("electron");
const path = require("path");

app.on("ready", () => {
  const mainWindow = new BrowserWindow({
    webPreferences: {
      //Both of these must be set like this in order to import node modules (like child_process) in the render code
      nodeIntegration: true,
      contextIsolation: false,
      preload: "preload.cjs"
    }
  })
  mainWindow.loadFile(path.join(__dirname, "public/index.html"));
  
  //Opens the dev tools window automatically
  // mainWindow.webContents.openDevTools();
});
