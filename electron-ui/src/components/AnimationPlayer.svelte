<script lang="ts">
  import ColorGrid from "./ColorGrid.svelte";

  let colorGrid = [];
  export let width;
  export let height;
  export let backgroundColor;
  export let cellSize;
  export let borderThickness;
  export let borderColor;
  export let cellSpacing;
  export let getColor: (pieceName: string) => string;

  export let frames;
  export let frameDelay;
  export let frameIndex = 0;

  let animationInterval;

  //Apply new frameDelay whenever it changes by re-creating the interval (restart)
  $: {
    frameDelay;
    restart();
  }

  //Start from frame 0 (reset) whenever the animation itself changes
  $: {
    frames;
    reset();
  }

  function displayFrame(frame) {
    // Build the frame
    let newColorGrid = [];
    let colorIndexGrid = frame;
    for (let i = 0; i < colorIndexGrid.length; i++) {
      let colorRow = [];
      for (let j = 0; j < colorIndexGrid[i].length; j++) {
        colorRow.push(getColor(colorIndexGrid[i][j]));
      }
      newColorGrid.push(colorRow);
    }

    //Set the colorGrid var to trigger Svelte autoupdate
    colorGrid = newColorGrid;
  }

  export function pause() {
    clearInterval(animationInterval);
  }

  export function restart() {
    pause();
    resume();
  }

  export function reset() {
    pause();
    frameIndex = 0;
    resume();
  }

  export function resume() {
    animationInterval = setInterval(() => {
      if (frames && frames.length) {
        //Display the current frame
        displayFrame(frames[frameIndex]);

        //Move to the next frame
        frameIndex = (frameIndex + 1) % frames.length;
      }
    }, frameDelay);
  }

  export function clear() {
    //Build a frame of all background and display it
    displayFrame(
      Array.from({ length: height + 6 }, () =>
        Array.from({ length: width }, () => backgroundColor)
      )
    );
  }

  export function stop() {
    pause();
    frameIndex = 0;
    clear();
  }
</script>

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

<style>
</style>
