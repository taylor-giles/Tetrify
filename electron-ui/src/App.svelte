<script lang="ts">
  import ToggleGrid from "./components/ToggleGrid.svelte";
  import {
    runEngine,
    stopAllChildren,
    getNumCores,
  } from "../../engine/runEngine.cjs";
  import ColorGrid from "./components/ColorGrid.svelte";
  import AnimationPlayer from "./components/AnimationPlayer.svelte";
  import OptionsPanel from "./components/OptionsPanel.svelte";

  let grid = [];
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
  let frameDelay = 0;

  let falsePositives = 0;
  let falseNegatives = 0;
  let enforceGravity = true;
  let numThreads = getNumCores() / 2;
  let removeDuplicates = true;

  let isRunning = false;
  let timeTakenStr = "0";
  let simulationTimer = null;
  let showLastFrames = false;
  let animations = [];
  let lastFrames = [];
  let lastFrameHashes = [];
  let animationDisplay; //Reference to the AnimationPlayer (gets bound later)

  //The number of the current animation being shown. 
  //Note that this is 1-indexed, to make displaying easier - use playAnimation(currAnimationNumber-1)
  let currAnimationNumber = -1;

  //To play an animation, just set this variable. The AnimationPlayer will auto-update.
  let currAnimation;

  //Sets the currAnimation variable to trigger an update of the AnimationPlayer.\
  function playAnimation(index){
    currAnimation = showLastFrames ? lastFrames[index] : animations[index];
  }

  //Automatically play animation when animation number or showLastFrames setting changes
  $: {
    showLastFrames;
    currAnimationNumber;
    playAnimation(currAnimationNumber-1);
  }

  //Make sure animation number stays within bounds
  $: if (!currAnimationNumber || currAnimationNumber < 1) {
    currAnimationNumber = 1;
  }
  $: if (currAnimationNumber > animations.length) {
    currAnimationNumber = animations.length;
  }

  // Compute frame delay from selected animation speed
  $: frameDelay = 1000 - animationSpeed * 10;

  /**
   * Runs when simulation successfully produces an animation
   * @param animationFrames A list of width x height frames where each element in the frame contains the name of the piece used to fill that slot
   */
  function onSuccess(animationFrames, time) {
    let lastFrame = animationFrames[animationFrames.length-1]

    //Add this animation to the list if either allowing duplicates or there is no other known animation with the same last frame as this animation
    if(!removeDuplicates || !lastFrameHashes.includes(JSON.stringify(lastFrame))){
      animations = [...animations, animationFrames];
      lastFrames = [...lastFrames, [lastFrame]]
      lastFrameHashes.push(JSON.stringify(lastFrame))
    }

    //If nothing is currently playing, play the first animation
    if (currAnimationNumber < 1) {
      playNextAnimation();
    }
  }

  /**
   * Runs when simulation finishes, meaning all threads exited.
   */
  function onEnd() {
    isRunning = false;

    //Stop the timer
    clearInterval(simulationTimer);
  }

  function onFailure(time) {}

  function runSimulation() {
    isRunning = true;
    clearAnimations();
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
    simulationTimer = setInterval(() => {
      timeTakenStr = ((Date.now() - timeStart) / 1000).toFixed(2);
    }, 50);
  }

  function invertGrid() {
    for (let i = 0; i < height; i++) {
      for (let j = 0; j < width; j++) {
        grid[i][j] = !grid[i][j];
      }
    }
    grid = grid;
  }

  function clearAnimations() {
    //Stop the animation
    animationDisplay.stop();

    //Reset animation number
    currAnimationNumber = 0;

    //Clear animations lists
    animations = [];
    lastFrames = [];
    lastFrameHashes = [];
  }

  function playNextAnimation() {
    currAnimationNumber = (currAnimationNumber + 1) % (animations.length+1);
  }

  function playPrevAnimation() {
    currAnimationNumber =
      (((currAnimationNumber - 1) % (animations.length+1)) + (animations.length+1)) %
      (animations.length+1);
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
        <div>
          Animations found: {animations.length}
        </div>
        <button on:click={stopAllChildren}> Stop </button>
      {/if}
    </div>
    <div id="preview-label">Preview:</div>

    <AnimationPlayer
      bind:this={animationDisplay}
      frames={currAnimation}
      {width}
      {height}
      {backgroundColor}
      {cellSize}
      {cellSpacing}
      {borderColor}
      {borderThickness}
      {frameDelay}
      {getColor}
    />
    <div id="preview-buttons-container">
      <button
        class="direction-button"
        disabled={animations.length <= 1}
        on:click={playPrevAnimation}
      >
        &lt;
      </button>
      <div>
        <input
          type="number"
          min="1"
          max={animations.length}
          bind:value={currAnimationNumber}
          id="animation-number-input"
          disabled={animations.length <= 1}
        />
        / {animations.length}
      </div>
      <button
        class="direction-button"
        disabled={animations.length <= 1}
        on:click={playNextAnimation}
      >
        &gt;
      </button>
    </div>
    <tr>
      <td>
          <div>Show Only Last Frames:</div>
      </td>
      <td>
          <input
              type="checkbox"
              bind:checked={showLastFrames}
              class="checkbox-input"
          />
      </td>
  </tr>
  </div>

  <OptionsPanel
    bind:isRunning
    bind:falsePositives
    bind:falseNegatives
    bind:enforceGravity
    bind:numThreads
    bind:removeDuplicates
    bind:colors
    bind:height
    bind:width
    bind:backgroundColor
    bind:borderColor
    bind:borderThickness
    bind:cellSize
    bind:cellSpacing
    bind:animationSpeed
  />
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
  #preview-label {
    margin-top: 50px;
  }
  .direction-button {
    background-color: transparent;
    border: none;
    font-family: "Courier New", Courier, monospace;
  }
  #animation-number-input {
    width: 75px;
    margin: 0px;
  }
  #preview-buttons-container {
    display: flex;
    width: 100%;
    justify-content: space-around;
    margin-top: 5px;
  }
</style>
