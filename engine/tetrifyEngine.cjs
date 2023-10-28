const { spawn } = require('node:child_process');
const os = require('node:os');
const path = require('node:path');

const EOF = "<EOF>"
const NUM_ADDED_ROWS = 6;

//Determine location of engine dir
const ENGINE_DIR = path.join(process.env.NODE_ENV ? '.' : process.resourcesPath ?? ".", 'engine')

//An array containing child process objects
let children = []

// A dictionary where the keys are PIDs and the values are strings containing the current message buffer for that child process
let buffers = {}

//These 3 functions assume that the engine is running on local hardware. The client should not use these directly - use the definitions in engineUtils instead.
function _getNumCores() {
  return os.cpus().length;
}

function _stopEngine() {
  children.forEach((child) => child.kill())
}

function _runEngine(grid, falsePositives, falseNegatives, enforceGravity, reduceWellsAndTowers, onSuccess, onEnd, numThreads = _getNumCores()) {
  //Add six rows to the top of the grid to allow for block spawning
  let new_grid = []
  for (let i = 0; i < NUM_ADDED_ROWS; i++) {
    new_grid.push(new Array(grid[0].length).fill(false))
  }
  new_grid.push(...grid)
  grid = new_grid

  let newChildren = []
  for (let childNum = 0; childNum < numThreads; childNum++) {
    const childProcess = spawn("python3", [path.join(ENGINE_DIR, 'tetrify_driver.py')]);
    newChildren.push(childProcess)
    children.push(childProcess)
    buffers[childProcess.pid] = ""
  }

  for (let childProcess of newChildren) {
    // Event handlers for process output
    childProcess.stdout.on("data", (msg) => {
      buffers[childProcess.pid] += msg //Add to buffer
      if (msg.includes(EOF)) {
        msg = buffers[childProcess.pid].replace(EOF, "")
        buffers[childProcess.pid] = "" //Clear buffer
        try {
          let data = JSON.parse(msg);

          //Log messages
          if ("log" in data) {
            console.log(`[${childProcess.pid}] ${data.log}`)
          }

          //Frames (animation finding was successful)
          if ("frames" in data) {
            console.log(`[${childProcess.pid}] Animation found`);
            onSuccess(data.frames);
          }
        } catch (e) {
          console.error(e);
          console.log(`[${childProcess.pid}] ${msg}`);
        }
      }
    });

    childProcess.stderr.on("data", (data) => {
      console.error(`[${childProcess.pid}] Error: ${data}`);
    });

    childProcess.on("close", (code) => {
      if (code === null) {
        console.log(`[${childProcess.pid}] Child process interrupted`);
      } else {
        console.log(`[${childProcess.pid}] Child process exited with code ${code}`);
      }

      //Remove this child from the list of children and buffer dictionary
      children.splice(children.indexOf(childProcess), 1);
      newChildren.splice(newChildren.indexOf(childProcess), 1);
      delete buffers[childProcess.pid];

      //Trigger end event if no more children FROM THIS SESSION are running
      if (newChildren.length <= 0) {
        onEnd();
      }
    });

    //Send the data over stdin
    childProcess.stdin.write(JSON.stringify({ grid: grid, false_positives: falsePositives, false_negatives: falseNegatives, enforce_gravity: enforceGravity, reduce_Is: reduceWellsAndTowers }));
    childProcess.stdin.end();
  }
  return newChildren;
}

module.exports = {_runEngine, _stopEngine, _getNumCores}