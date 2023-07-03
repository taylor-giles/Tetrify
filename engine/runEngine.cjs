const { spawn } = window.require('node:child_process');

const EOF = "<EOF>"

export function runEngine(grid, onSuccess){
  //Add six rows to the top of the grid to allow for block spawning
  let new_grid = []
  for(let i = 0; i < 6; i++){
    new_grid.push(new Array(grid[0].length).fill(false))
  }
  new_grid.push(...grid)
  grid = new_grid

  //An array containing child process objects
  let children = []

  // A dictionary where the keys are PIDs and the values are strings containing the current message buffer for that child process
  let buffers = {}

  for(let childNum = 0; childNum < 12; childNum++){
    const childProcess = spawn("python", ["../engine/test.py"]);
    children.push(childProcess)
    buffers[childProcess.pid] = ""
  }

  for(let childProcess of children){
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
      console.log(`[${childProcess.pid}] Child process exited with code ${code}`);

      //Kill all the other children (if one process ended, either the animation was successfully found, or it is not possible.)
      children.forEach((child) => child.kill())
    });

    //Send the data over stdin
    childProcess.stdin.write(JSON.stringify(grid));
    childProcess.stdin.end();
  }
}
