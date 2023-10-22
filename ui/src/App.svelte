<script context="module" lang="ts">
  export enum AppContextMode {
    DRAWING,
    RUNNING,
    STOPPED,
  }

  //30x30 is the largest possible grid that can be animated without running into recursion errors
  //Any width lower than 8 causes buggy behavior
  export const MAX_WIDTH = 30;
  export const MAX_HEIGHT = 30;
  export const MIN_WIDTH = 8;
  export const MIN_HEIGHT = 1;
</script>

<script lang="ts">
  import ToggleGrid from "./components/ToggleGrid.svelte";
  import { runEngine, stopEngine } from "../../engine/runEngine.cjs";
  import AnimationPlayer from "./components/AnimationPlayer.svelte";
  import OptionsPanel from "./components/OptionsPanel.svelte";
  import HelpText from "./components/HelpText.svelte";
  import StopConditionSelector from "./components/StopConditionSelector.svelte";

  let currentMode: AppContextMode = AppContextMode.DRAWING;

  //Canvas & display options
  let grid = [];
  let backgroundColor = "#000000";
  let borderColor = "#000000";
  let borderThickness = 1;
  let cellHeight = 20;
  let cellWidth = 20;
  let colors = {
    T: "#FF00FF",
    L: "#FFAA00",
    S: "#00FF00",
    O: "#FFFF00",
    I: "#00FFFF",
    Z: "#FF0000",
    J: "#0000FF",
  };
  let width = 16;
  let height = 16;

  //Simulation options
  let falsePositives = 0;
  let falseNegatives = 0;
  let enforceGravity = true;
  let numThreads = 1;
  let removeDuplicates = true;
  let reduceWellsAndTowers = false;

  //Simulation/animation variables
  let timeTakenStr = "0";
  let simulationTimer = null;
  let useAutoStop = false;
  let stopCondition: { time: number; animations: number } = {
    time: null,
    animations: null,
  };
  let showLastFrames = false;
  let gifProgress: string | null = null;
  let animations = [];
  let lastFrameHashes = [];
  let animationSpeed = 99;
  let frameDelay = 0;
  let animationDisplay; //Reference to the AnimationPlayer (gets bound later)
  let canvas; //Reference to the ToggleGrid art canvas (gets bound later)

  //The number of the current animation being displayed.
  //Note that this is 1-indexed, to make displaying easier - use playAnimation(currAnimationNumber-1)
  let currAnimationNumber = 0;

  //The AnimationPlayer auto-updates to display this animation
  let currAnimation;

  //Sets the currAnimation variable to trigger an update of the AnimationPlayer.
  function playAnimation(index: number) {
    currAnimation =
      showLastFrames && animations.length > 0
        ? [animations[index][animations[index]?.length - 1]]
        : animations[index];
  }

  //Automatically play animation when animation number or showLastFrames setting changes
  $: {
    showLastFrames;
    currAnimationNumber;
    playAnimation(currAnimationNumber - 1);
  }

  //Make sure animation number stays within bounds
  $: if (!currAnimationNumber || currAnimationNumber < 1) {
    currAnimationNumber = 1;
  }
  $: if (currAnimationNumber > animations.length) {
    currAnimationNumber = animations.length;
  }

  // Compute frame delay from selected animation speed
  $: frameDelay = 315 - animationSpeed * 3;

  /**
   * Clears canvas and animations, and starts drawing mode
   */
  function restart() {
    clearAnimations();
    canvas.defineGrid();
    currentMode = AppContextMode.DRAWING;
  }

  /**
   * Runs when simulation successfully produces an animation.
   * Adds the new animation to the list if it is not a duplicate or duplicates are allowed.
   * @param animationFrames A list of width x height frames where each element in the frame contains the name of the piece used to fill that slot
   */
  function onSuccess(animationFrames) {
    let lastFrame = animationFrames[animationFrames.length - 1];

    //Add this animation to the list if either allowing duplicates or there is no other known animation with the same last frame as this animation
    if (
      !removeDuplicates ||
      !lastFrameHashes.includes(JSON.stringify(lastFrame))
    ) {
      animations = [...animations, animationFrames];
      lastFrameHashes.push(JSON.stringify(lastFrame));
    }

    //If nothing is currently playing, play the first animation
    if (currAnimationNumber < 1) {
      playNextAnimation();
    }

    //Check the animations stop condition
    if (
      useAutoStop &&
      stopCondition.animations &&
      animations.length > stopCondition.animations
    ) {
      stopEngine();
    }
  }

  /**
   * Runs when simulation finishes, meaning all threads exited.
   */
  function onEnd() {
    currentMode = AppContextMode.STOPPED;

    //Stop the timer
    clearInterval(simulationTimer);
  }

  function runSimulation() {
    currentMode = AppContextMode.RUNNING;
    clearAnimations();
    runEngine(
      grid,
      falsePositives,
      falseNegatives,
      enforceGravity,
      reduceWellsAndTowers,
      onSuccess,
      onEnd,
      numThreads
    );

    // Clear stop conditions
    useAutoStop = false;
    stopCondition = {time: null, animations: null}

    // Start the timer
    let timeStart = Date.now();
    simulationTimer = setInterval(() => {
      let seconds = (Date.now() - timeStart) / 1000;
      let minutes = (seconds / 60) | 0;
      let hours = (minutes / 60) | 0;
      timeTakenStr =
        (hours > 0 ? `${hours}h ` : "") +
        (minutes > 0 ? `${minutes - hours * 60}m ` : "") +
        `${(seconds - minutes * 60).toFixed(2)}s`;

      //Check the stop condition time
      if (useAutoStop && stopCondition.time && seconds >= stopCondition.time) {
        stopEngine();
      }
    }, 50);
  }

  function clearAnimations() {
    //Stop the animation
    animationDisplay?.stop();

    //Reset animation number
    currAnimationNumber = 0;

    //Clear animations lists
    animations = [];
    lastFrameHashes = [];
  }

  function playNextAnimation() {
    currAnimationNumber = (currAnimationNumber + 1) % (animations.length + 1);
  }

  function playPrevAnimation() {
    currAnimationNumber =
      currAnimationNumber == 1 ? animations.length : currAnimationNumber - 1;
  }

  function getColor(pieceName) {
    return colors[pieceName] ?? backgroundColor;
  }

  function onGifProgressUpdate(e) {
    gifProgress = e.detail;
  }
</script>

<main>
  <!-- Art -->
  <div id="art-container">
    {#if currentMode == AppContextMode.DRAWING}
      <div>Draw Here:</div>
    {/if}

    <ToggleGrid
      width={width <= MAX_WIDTH ? width : MAX_WIDTH}
      height={height <= MAX_HEIGHT ? height : MAX_HEIGHT}
      bind:grid
      disabled={currentMode != AppContextMode.DRAWING}
      bind:this={canvas}
    />
    <div id="result-text-panel">
      {#if currentMode == AppContextMode.RUNNING}
        <div>
          Simulating. Time elapsed: {timeTakenStr}
        </div>
        <div>
          Animations found: {animations.length}
        </div>
      {:else if currentMode == AppContextMode.STOPPED}
        <div><b>Simulation complete.</b> Time elapsed: {timeTakenStr}</div>
        <div>
          Animations found: {animations.length}
        </div>
      {/if}
    </div>
    <div id="button-panel">
      {#if currentMode == AppContextMode.DRAWING}
        <button
          on:click={() => {
            canvas.invertGrid();
          }}
        >
          Invert
        </button>
        <button on:click={restart}> Clear </button>
        <button on:click={runSimulation}> Animate! </button>
      {:else if currentMode == AppContextMode.RUNNING}
        <tr>
          <td>
            <input
              type="checkbox"
              bind:checked={useAutoStop}
              class="checkbox-input"
            />
          </td>
          <td>
            <div> Automatic Stop </div>
          </td>
        </tr>
        {#if useAutoStop}
          <StopConditionSelector
            on:apply={(e) => {
              stopCondition = e.detail;
            }}
          />
        {/if}
        <button on:click={stopEngine}> Stop Now </button>
      {:else if currentMode == AppContextMode.STOPPED}
        <button on:click={runSimulation}> Re-Animate</button>
        <button
          on:click={() => {
            clearAnimations();
            currentMode = AppContextMode.DRAWING;
          }}
        >
          Edit Drawing
        </button>
      {/if}
    </div>
  </div>

  {#if currentMode != AppContextMode.DRAWING}
    <!-- Preview -->
    <div id="preview-container">
      <div id="preview-label">Preview:</div>
      <AnimationPlayer
        bind:this={animationDisplay}
        frames={currAnimation}
        {width}
        height={height + 6}
        {backgroundColor}
        {cellHeight}
        {cellWidth}
        {borderColor}
        {borderThickness}
        {frameDelay}
        {getColor}
        on:gifProgressUpdate={onGifProgressUpdate}
      />
      {#if gifProgress}
        <div>
          Generating GIF. {gifProgress}
        </div>
      {:else}
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
            <input
              type="checkbox"
              bind:checked={showLastFrames}
              class="checkbox-input"
              disabled={animations.length < 1}
            />
          </td>
          <td>
            <div>Show Only Final Board State</div>
          </td>
        </tr>

        <div>
          <button
            disabled={animations.length < 1}
            on:click={() => {
              gifProgress = "Generating GIF....";
              animationDisplay.save();
            }}
          >
            {#if showLastFrames}
              Save Image
            {:else}
              Save Animation GIF
            {/if}
          </button>
        </div>
      {/if}
    </div>
  {:else}
    <div id="help-text">
      <HelpText />
    </div>
  {/if}

  <!-- Options -->
  <OptionsPanel
    bind:currentMode
    bind:falsePositives
    bind:falseNegatives
    bind:enforceGravity
    bind:reduceWellsAndTowers
    bind:numThreads
    bind:removeDuplicates
    bind:colors
    bind:height
    bind:width
    bind:backgroundColor
    bind:borderColor
    bind:borderThickness
    bind:cellWidth
    bind:cellHeight
    bind:animationSpeed
  />
</main>

<style>
  main {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: top;
  }
  input {
    margin: 0px;
  }

  #result-text-panel {
    margin-top: 5px;
  }
  #button-panel {
    margin-top: 5px;
  }
  #art-container {
    height: max-content;
    max-width: calc(100% - 400px);
    padding: 20px;
    overflow-y: auto;
  }
  #help-text {
    flex: 1;
    padding: 20px;
    padding-top: 5px;
    border: 2px solid black;
    border-radius: 20px;
    overflow-y: auto;
    scrollbar-width: thin;
    margin-inline: 30px;
    height: 100%;
    box-sizing: border-box;
  }
  #animation-number-input {
    width: 75px;
    margin: 0px;
  }
  #preview-buttons-container {
    display: flex;
    width: 100%;
    justify-content: center;
    margin-top: 5px;
  }
  .direction-button {
    background-color: transparent;
    border: none;
    font-family: "Courier New", Courier, monospace;
  }
</style>
