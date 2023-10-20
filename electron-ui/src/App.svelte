<script context="module" lang="ts">
  export enum AppContextMode {
    DRAWING,
    RUNNING,
    STOPPED,
  }

  //30x30 is the largest possible grid that can be animated without running into recursion errors
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

  let currentMode: AppContextMode = AppContextMode.DRAWING;

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
  let animationSpeed = 99;
  let frameDelay = 0;

  let falsePositives = 0;
  let falseNegatives = 0;
  let enforceGravity = true;
  let numThreads = 1;
  let removeDuplicates = true;

  let timeTakenStr = "0";
  let simulationTimer = null;
  let showLastFrames = false;
  let animations = [];
  let lastFrameHashes = [];
  let animationDisplay; //Reference to the AnimationPlayer (gets bound later)
  let canvas; //Reference to the ToggleGrid art canvas (gets bound later)

  //The number of the current animation being displayed.
  //Note that this is 1-indexed, to make displaying easier - use playAnimation(currAnimationNumber-1)
  let currAnimationNumber = 0;

  //To play an animation, just set this variable. The AnimationPlayer will auto-update.
  let currAnimation;

  //Sets the currAnimation variable to trigger an update of the AnimationPlayer.
  function playAnimation(index: number) {
    currAnimation = showLastFrames
      ? [animations[index][animations[index].length - 1]]
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
  $: frameDelay = 1000 - animationSpeed * 10;

  function restart() {
    clearAnimations();
    canvas.defineGrid();
    currentMode = AppContextMode.DRAWING;
  }

  /**
   * Runs when simulation successfully produces an animation
   * @param animationFrames A list of width x height frames where each element in the frame contains the name of the piece used to fill that slot
   */
  function onSuccess(animationFrames, time) {
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
  }

  /**
   * Runs when simulation finishes, meaning all threads exited.
   */
  function onEnd() {
    currentMode = AppContextMode.STOPPED;

    //Stop the timer
    clearInterval(simulationTimer);
  }

  function onFailure(time) {}

  function runSimulation() {
    currentMode = AppContextMode.RUNNING;
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
</script>

<main>
  <!-- Art -->
  <div id="art-container">
    {#if currentMode == AppContextMode.DRAWING}
      <div>Draw Here:</div>
    {/if}

    <ToggleGrid
      {width}
      bind:height
      bind:grid
      disabled={currentMode != AppContextMode.DRAWING}
      bind:this={canvas}
    />
    <div id="result-text-panel">
      {#if currentMode == AppContextMode.RUNNING}
        <div>
          Simulating. Time elapsed: {timeTakenStr}s
        </div>
        <div>
          Animations found: {animations.length}
        </div>
      {:else if currentMode == AppContextMode.STOPPED}
        <div><b>Simulation complete.</b> Time elapsed: {timeTakenStr}s</div>
        <div>
          Animations found: {animations.length}
        </div>
      {/if}
    </div>
    <div id="button-panel">
      {#if currentMode == AppContextMode.DRAWING}
        <button on:click={invertGrid}> Invert </button>
        <button on:click={restart}> Clear </button>
        <button on:click={runSimulation}> Animate! </button>
      {:else if currentMode == AppContextMode.RUNNING}
        <button on:click={stopEngine}> Stop </button>
      {:else if currentMode == AppContextMode.STOPPED}
        <button on:click={runSimulation}> Re-Animate</button>
        <button
          on:click={() => {
            currentMode = AppContextMode.DRAWING;
          }}
        >
          Edit Drawing
        </button>
        <button
          on:click={() => {
            animationDisplay.saveGif();
          }}
        >
          jfklds
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
          <input
            type="checkbox"
            bind:checked={showLastFrames}
            class="checkbox-input"
          />
        </td>
        <td>
          <div>Show Only Final Board State</div>
        </td>
      </tr>
    </div>
  {:else}
    <div id="help-text">
      <h2>Welcome to the Tetrify Art Creator!</h2>
      <p>
        This app is designed to provide an easy and intuitive interface for
        generating Tetra-themed animations. It uses an optimized semi-random
        approach for generating animations, by simulating many possible
        sequences of block positions until a board state matching the input
        drawing is found. Read this guide for instructions on using this app and
        descriptions of the options and processes involved.
      </p>

      <h4>Drawing</h4>
      <p>
        Click and drag in the canvas on the left to draw the desired end-goal
        image (black cells are background, and white cells are part of the image
        to Tetrify). The size of the canvas can be changed using the Canvas
        Height and Canvas Width options on the right, but note that the canvas
        will be cleared whenever it is resized. Also note that six rows will be
        added to the top of the canvas in all generated animations to allow room
        for the blocks to be created, rotated, and moved. If you want to start
        over at any point, the "Clear" button will reset the canvas back to the
        default blank state. When you're satisfied, press the "Animate!" button,
        and the simulator will begin looking for valid ways to Tetrify your
        artwork.
      </p>

      <h4>Viewing Results & Customization</h4>
      <p>
        As valid animations are simulated, they will appear in the preview
        window. You can customize the appearance of the animations using the
        Block Colors and Display Options settings on the right. If multiple
        valid animations are found, you can use the buttons at the bottom of the
        preview window to see them all. To see only the final "Tetrified" image,
        toggle on the "Show Only Final Board State" option.

        It is important to note that many drawings may take hours or longer to
        fully simulate all animation possibilities. Therefore, it is recommended
        to interrupt the simulation by pressing "Stop" once satisfied with the
        generated animations.
      </p>
      <p>
        
      </p>

      <h4>Simulation Options</h4>
      <p>
        Some images are not "Tetrify-able" using the default settings, for
        various reasons. The Simulation Options on the right are designed to
        offer greater flexibility, allowing the simulation to "bend the rules"
        in certain ways to make it possible to Tetrify a wider range of images,
        through some compromises. Use this guide to better understand why some
        images are not "Tetrify-able" and how to use these options to work
        around those restrictions:
        <li>
          <b>False Positives</b> - The number of "extra" background cells that the
          animation is "allowed" to fill with blocks. For example, an image consisting
          of a line of exactly three cells would not be "Tetrify-able", because there
          is no Tetrimino that consists of only three cells. However, allowing at
          least one "false positive" would mean that an extra background cell could
          be filled, and an animation could be generated. In general, increasing
          this value will increase the likelihood that an animation will be found,
          while sacrificing image integrity.
        </li>
        <li>
          <b>False Negatives</b> - The number of image cells that the animation is
          "allowed" to omit. For example, an image consisting of a line of exactly
          five cells would not be "Tetrify-able", because there is no way to fill
          exactly five cells with Tetriminoes. However, allowing at least one "false
          negative" would mean that the extra cell could be left as background, and
          an animation could be generated. In general, increasing this value will
          increase the likelihood that an animation will be found, while sacrificing
          image integrity.
        </li>
        <li>
          <b>Enforce Gravity</b> - If this option is enabled, then all blocks in
          the simulation must fall until landing on the bottom of the canvas or another
          block. However, by disabling this option, it is possible to create animations
          in which blocks are allowed to remain floating - in this case, the blocks
          will fall until they either reach the desired location or land on another
          block, then stop. In general, disabling this option will increase the likelihood
          that an animation will be found, but the results may look somewhat strange.
        </li>
        <li>
          <b>Number of Threads</b> - Since this app's simulations involve randomized
          elements, running multiple simulations at the same time can result in finding
          multiple different animations more quickly. This option allows you to specify
          how many distinct threads should be used to run simulations. Note that
          this value cannot exceed the number of available CPU threads, and that
          increasing this value can result in high CPU usage.
        </li>
        <li>
          <b>Remove Duplicates</b> - It is possible that the simulation may encounter
          animations with identical final states or, if using multiple threads, identical
          animations. If this option is enabled, animations with end-states that
          have already been seen in previously-generated animations will not be saved
          or shown.
        </li>
      </p>
    </div>
  {/if}

  <!-- Options -->
  <OptionsPanel
    bind:currentMode
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
  h4 {
    margin-bottom: -15px;
  }
  li {
    margin-top: 8px;
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
