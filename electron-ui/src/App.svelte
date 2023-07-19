<script lang="ts">
  import ToggleGrid from "./components/ToggleGrid.svelte";
  import {
    runEngine,
    stopAllChildren,
    getNumCores,
  } from "../../engine/runEngine.cjs";
  import ColorGrid from "./components/ColorGrid.svelte";

  let grid = [];
  let colorIndexGrid = [];
  let backgroundColor = "#000000";
  let borderColor = "#000000";
  let borderThickness = 1;
  let cellSize = 20;
  let cellSpacing = 0;
  let colors = {
    T: "#FF00FF",
    J: "#FFAA00",
    L: "#00FF00",
    O: "#A06020",
    Z: "#00FFFF",
    S: "#FF0000",
    I: "#0000FF",
  };
  let width = 16;
  let height = 16;
  let animationSpeed = 90;
  let currAnimationNumber = 0;
  let colorGrid = [];

  let falsePositives = 0;
  let falseNegatives = 0;
  let enforceGravity = true;
  let numThreads = getNumCores() / 2;

  let isRunning = false;
  let didRun = false;
  let didSucceed = false;
  let timeTakenStr = "0";
  let simulationTimer = null;

  // Make sure option values stay defined & positive
  $: if (!falsePositives || falsePositives < 0) {
    falsePositives = 0;
  }
  $: if (!falseNegatives || falseNegatives < 0) {
    falseNegatives = 0;
  }
  $: if (!numThreads || numThreads < 1) {
    numThreads = 1;
  }
  $: if (numThreads > getNumCores()) {
    numThreads = getNumCores();
  }

  // Compute frame delay from selected animation speed
  $: frameDelay = 1000 - animationSpeed * 10;

  /**
   * Runs when simulation successfully produces an animation
   * @param animationFrames A list of width x height frames where each element in the frame contains the name of the piece used to fill that slot
   */
  function onSuccess(animationFrames, time) {
    didSucceed = true;
    currAnimationNumber++;
    playAnimation(animationFrames, currAnimationNumber);
  }

  function onEnd() {
    isRunning = false;

    //Stop the timer
    clearInterval(simulationTimer);
  }

  function onFailure(time) {}

  function runSimulation() {
    isRunning = true;
    didRun = true;
    stopAnimation();
    runEngine(
      grid,
      falsePositives,
      falseNegatives,
      enforceGravity,
      onSuccess,
      onFailure,
      onEnd,
      numThreads
    );

    // Start the timer
    let timeStart = Date.now();
    simulationTimer = setInterval(() => {timeTakenStr = ((Date.now() - timeStart) / 1000).toFixed(2);}, 50)
  }

  function invertGrid() {
    for (let i = 0; i < height; i++) {
      for (let j = 0; j < width; j++) {
        grid[i][j] = !grid[i][j];
      }
    }
    grid = grid;
  }

  function stopAnimation() {
    //Change animation number to stop the animation from playing
    currAnimationNumber++;

    // Reset display
    for (let i = 0; i < colorGrid.length; i++) {
      for (let j = 0; j < colorGrid[i].length; j++) {
        colorGrid[i][j] = backgroundColor;
      }
    }

    //Set the colorGrid var to trigger Svelte autoupdate
    colorGrid = colorGrid;
  }

  function playAnimation(frames, animationNumber = 0, frameIndex = 0) {
    if (animationNumber >= currAnimationNumber) {
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
      setTimeout(() => {
        playAnimation(
          frames,
          animationNumber,
          (frameIndex + 1) % frames.length
        );
      }, frameDelay);
    }
  }

  function getColor(pieceName) {
    return colors[pieceName] ?? backgroundColor;
  }
</script>

<main>
  <div id="art-container">
    <ToggleGrid {width} bind:height bind:grid bind:disabled={isRunning} />
    <div id="button-panel">
      {#if !isRunning}
        <button on:click={invertGrid}> Invert </button>
        <button on:click={runSimulation}> Animate! </button>
      {:else}
        <div>
          Simulating. Time elapsed: {timeTakenStr}s
        </div>
        <button on:click={stopAllChildren}> Cancel </button>
      {/if}
    </div>
    <div id="preview-label">Preview:</div>
    <ColorGrid
      bind:width
      height={height + 6}
      bind:grid={colorGrid}
      defaultColor={backgroundColor}
      cellWidth={`${cellSize}px`}
      cellHeight={`${cellSize}px`}
      cellBorder={`${borderThickness}px solid ${borderColor}`}
      cellMargin={`${cellSpacing}px`}
    />
  </div>

  <div id="options-container">
    <div class="region-header">Options</div>
    <div class="section-header">Simulation Options</div>
    {#if isRunning}
      <div>(Disabled while simulation is running)</div>
    {/if}
    <table>
      <tr>
        <td>
          <div class="option-label">False Positives:</div>
        </td>
        <td>
          <input
            type="number"
            min="0"
            bind:value={falsePositives}
            class="number-input"
            disabled={isRunning}
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">False Negatives:</div>
        </td>
        <td>
          <input
            type="number"
            min="0"
            bind:value={falseNegatives}
            class="number-input"
            disabled={isRunning}
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Enforce Gravity:</div>
        </td>
        <td>
          <input
            type="checkbox"
            bind:checked={enforceGravity}
            class="checkbox-input"
            disabled={isRunning}
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Number of Threads:</div>
        </td>
        <td>
          <input
            type="number"
            min="1"
            max={getNumCores()}
            bind:value={numThreads}
            class="number-input"
            disabled={isRunning}
          />
        </td>
      </tr>
    </table>

    <div class="section-header">Block Colors</div>
    <table>
      {#each Object.keys(colors) as blockName}
        <tr>
          <td>
            <div class="color-label">
              "{blockName}" Block:
            </div>
          </td>
          <td>
            <input
              type="color"
              bind:value={colors[blockName]}
              class="color-input"
            />
          </td>
        </tr>
      {/each}
    </table>
    <div class="section-header">Display Options</div>
    <table>
      <tr>
        <td>
          <div class="option-label">Canvas Height:</div>
        </td>
        <td>
          <input
            type="number"
            min="1"
            bind:value={height}
            class="number-input"
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Canvas Width:</div>
        </td>
        <td>
          <input
            type="number"
            min="4"
            bind:value={width}
            class="number-input"
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Background Color:</div>
        </td>
        <td>
          <input
            type="color"
            bind:value={backgroundColor}
            class="color-input"
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Border Color:</div>
        </td>
        <td>
          <input type="color" bind:value={borderColor} class="color-input" />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Border Thickness:</div>
        </td>
        <td>
          <input
            type="number"
            min="0"
            bind:value={borderThickness}
            class="number-input"
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Cell Size:</div>
        </td>
        <td>
          <input
            type="number"
            min="0"
            bind:value={cellSize}
            class="number-input"
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Cell Spacing:</div>
        </td>
        <td>
          <input
            type="number"
            min="0"
            bind:value={cellSpacing}
            class="number-input"
          />
        </td>
      </tr>
      <tr>
        <td>
          <div class="option-label">Animation Speed:</div>
        </td>
        <td>
          <input
            type="number"
            min="0"
            bind:value={animationSpeed}
            class="number-input"
          />
        </td>
      </tr>
    </table>
  </div>
</main>

<style>
  main {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  input {
    margin: 0px;
  }
  #art-container {
    height: 90vh;
    max-width: calc(100% - 400px);
    padding: 20px;
    overflow-y: auto;
  }
  #options-container {
    height: 90vh;
    width: 300px;
    padding: 20px;
    border: 2px solid black;
    border-radius: 20px;
    white-space: nowrap;
    overflow-y: auto;
    scrollbar-width: thin;
  }
  #preview-label {
    margin-top: 50px;
  }

  td {
    padding-bottom: 10px;
    padding-inline: 5px;
  }
  table {
    margin-bottom: 20px;
  }
  .number-input {
    width: 100px;
    margin: 0px;
  }
  .option-label {
    height: 100%;
  }
  .color-label {
    font-family: "Courier New", Courier, monospace;
    margin-left: 5px;
  }
  .region-header {
    font-weight: bold;
    font-size: 28px;
    text-align: center;
    width: 100%;
    margin-bottom: 10px;
  }
  .section-header {
    font-weight: bold;
    font-size: 20px;
  }
  .color-input {
    border: 1px;
    margin: 0px 0px 0px 15px;
    padding: 0;
    width: 100px;
    cursor: pointer;
  }
</style>
