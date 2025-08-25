const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { nodeIntegration: true, contextIsolation: false },
  });

  mainWindow.loadFile(path.join(__dirname, "dist/index.html"));
}

app.on("ready", () => {
  // Start Python FastAPI server
  pythonProcess = spawn("python", ["backend/app.py"], { shell: true });
  pythonProcess.stdout.on("data", (data) => console.log(data.toString()));
  pythonProcess.stderr.on("data", (data) => console.error(data.toString()));

  createWindow();
});

app.on("window-all-closed", () => {
  if (pythonProcess) pythonProcess.kill();
  if (process.platform !== "darwin") app.quit();
});
