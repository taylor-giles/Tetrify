const { spawn } = window.require('node:child_process');

const EOF = "<EOF>"

//An array containing child process objects
let children = []

// A dictionary where the keys are PIDs and the values are strings containing the current message buffer for that child process
let buffers = {}

export function stopAllChildren(){
  children.forEach((child) => child.kill())
}

export function runEngine(grid, onSuccess){
  //Add six rows to the top of the grid to allow for block spawning
  let new_grid = []
  for(let i = 0; i < 6; i++){
    new_grid.push(new Array(grid[0].length).fill(false))
  }
  new_grid.push(...grid)
  grid = new_grid

  let newChildren = []
  for(let childNum = 0; childNum < 12; childNum++){
    const childProcess = spawn("python", ["../engine/test.py"]);
    newChildren.push(childProcess)
    children.push(childProcess)
    buffers[childProcess.pid] = ""
  }

  for(let childProcess of newChildren){
    // Event handlers for process output
    childProcess.stdout.on("data", (msg) => {
      buffers[childProcess.pid] += msg //Add to buffer
      if(msg.includes(EOF)){
        msg = buffers[childProcess.pid].replace(EOF, "")
        buffers[childProcess.pid] = "" //Clear buffer
        try {
          let data = JSON.parse(msg)
  
          //Log messages
          if("log" in data){
            console.log(`[${childProcess.pid}] ${data.log}`)
          }
  
          //Frames (animation finding was successful)
          if ("frames" in data){
            console.log(`[${childProcess.pid}] Received animation frames: ${data.frames}`)
            onSuccess(data.frames)
          }
        } catch(e) {
          console.log(`[${childProcess.pid}] ${msg}`);
        }
      }
    });

    childProcess.stderr.on("data", (data) => {
      console.error(`[${childProcess.pid}] Error: ${data}`);
    });

    childProcess.on("close", (code) => {
      if(code === null){
        console.log(`[${childProcess.pid}] Child process interrupted`);
      } else {
        console.log(`[${childProcess.pid}] Child process exited with code ${code}`);
      }
      
      //Remove this child from the list of children and buffer dictionary
      children.splice(children.indexOf(childProcess), 1)
      delete buffers[childProcess.pid]

      //Kill all the other children (if one process ended, either the animation was successfully found, or it is not possible.)
      stopAllChildren();
    });

    //Send the data over stdin
    childProcess.stdin.write(JSON.stringify({grid: grid, false_positives: 0, false_negatives: 0}));
    childProcess.stdin.end();
  }
}