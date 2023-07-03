<script lang="ts">
  import ToggleGrid from "./components/ToggleGrid.svelte";
  import { runEngine } from "../../engine/runEngine.cjs";
  import ColorGrid from "./components/ColorGrid.svelte";

  let grid = [];
  let colorIndexGrid = [];
  const DEFAULT_COLOR = "#FFFFFF";
  let colors = {
    "T": "#FF00FF",
    "J": "#FFAA00",
    "L": "#00FF00",
    "Z": "#00FFFF",
    "S": "#FF0000",
    "I": "#0000FF",
    "O": "#905010",
    
    "A": "#FFFFFF",
    "P": "#999999"
  };
  let width = 8,
    height = 8;
  let frameDelay = 100;
  let currAnimationNumber = 0;

  let colorGrid = [];

  /**
   * Runs when simulation successfully produces an animation
   * @param animationFrames A list of width x height frames where each element contains the name of the piece used to fill that slot
   */
  function onSuccess(animationFrames) {
    // Start the animation
    startAnimation(animationFrames) 
  }

  function runSimulation() {
    runEngine(grid, onSuccess);
  }

  function startAnimation(frames) {
    playAnimation(frames, currAnimationNumber++)
  }

  function playAnimation(frames, animationNumber = 0, frameIndex = 0, frameDelay = getFrameDelay()) {  
    if(animationNumber >= currAnimationNumber-1){
      // Build the frame
      let newColorGrid = [];
      colorIndexGrid = frames[frameIndex];
      for (let i = 0; i < colorIndexGrid.length; i++) {
        let colorRow = [];
        for (let j = 0; j < colorIndexGrid[i].length; j++) {
          colorRow.push(getColor(colorIndexGrid[i][j]));
        }
        newColorGrid.push(colorRow);
      }

      //Set the colorGrid var to trigger Svelte autoupdate
      colorGrid = newColorGrid;

      //Set the timeout to display the next frame
      let nextFrameDelay = getFrameDelay() //This function call is necessary so that the frame delay will change if updated by user during animation
      setTimeout(() => {playAnimation(frames, animationNumber, (frameIndex+1) % frames.length, nextFrameDelay)}, frameDelay);
    }
  }

  function getColor(pieceName) {
    return colors[pieceName] ?? DEFAULT_COLOR;
  }

  /**
   * A getter function is necessary for use inside setTimeout callback
   */
  function getFrameDelay() {
    return frameDelay;
  }
</script>

<main>
  <div />
  <ToggleGrid bind:width bind:height bind:grid />
  <div id="preview-label-spacer">
    Preview:
  </div>
  <ColorGrid bind:width height={height+6} bind:grid={colorGrid} />

  <button on:click={runSimulation}> Animate! </button>
</main>

<style>
  #preview-label-spacer{
    margin-top: 50px;
    background-color: "red"
  }
</style>
