const { spawn } = window.require('node:child_process');

export function runEngine(grid, onSuccess){
    const childProcess = spawn("python", ["../engine/test.py"]);

    // Event handlers for process output
    childProcess.stdout.on("data", (msg) => {
      try {
        let data = JSON.parse(msg)
        console.log(`Received animation frames: ${msg}`)
        onSuccess(data.frames)
        
      } catch(e) {
        console.log(`Output: ${msg}`);
      }
    });
    
    childProcess.stderr.on("data", (data) => {
      console.error(`Error: ${data}`);
    });
    
    childProcess.on("close", (code) => {
      console.log(`Child process exited with code ${code}`);
    });

    //Send the data over stdin
    childProcess.stdin.write(JSON.stringify(grid));
    childProcess.stdin.end();
}
