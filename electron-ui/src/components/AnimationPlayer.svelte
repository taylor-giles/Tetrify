<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import {
    makeAndSaveGif,
    generateImageURL,
    saveImageFromURL,
  } from "../tetrifyImageUtils";
  import ColorGrid from "./ColorGrid.svelte";
  const dispatch = createEventDispatcher();

  let colorGrid = [];
  export let width: number;
  export let height: number;
  export let backgroundColor: string;
  export let cellHeight: number;
  export let cellWidth: number;
  export let borderThickness: number;
  export let borderColor: string;

  export let getColor: (cellValue: any) => string;

  export let frames: number[][];
  export let frameDelay: number;
  export let frameIndex = 0;

  let animationInterval: any;
  let mainView: any; //Reference to ColorGrid (gets bound later)

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

  function computeColorGrid(frame) {
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
    return newColorGrid;
  }

  function displayFrame(frame) {
    //Set the colorGrid var to trigger Svelte autoupdate
    colorGrid = computeColorGrid(frame);
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
      Array.from({ length: height }, () =>
        Array.from({ length: width }, () => backgroundColor)
      )
    );
  }

  export function stop() {
    pause();
    frameIndex = 0;
    clear();
  }

  export async function save() {
    //Generate GIF frames
    let frameURLs = [];
    for (let frame of frames) {
      frameURLs.push(
        await generateImageURL(
          computeColorGrid(frame),
          borderColor,
          borderThickness,
          cellHeight,
          cellWidth
        )
      );
      dispatch("gifProgressUpdate", `Generating: ${((frames.indexOf(frame) / frames.length) * 100).toFixed(0)}%`);
    }
    dispatch("gifProgressUpdate", null)

    //Save the gif (or image, if there is only one frame)
    if (frameURLs.length > 1) {
      makeAndSaveGif(frameURLs, frameDelay, (update) => {dispatch("gifProgressUpdate", update)});
    } else {
      saveImageFromURL(frameURLs[0]);
    }
  }
</script>

<ColorGrid
  bind:this={mainView}
  {width}
  {height}
  bind:grid={colorGrid}
  defaultColor={backgroundColor}
  {cellWidth}
  {cellHeight}
  cellBorderThickness={borderThickness}
  cellBorderColor={borderColor}
/>

<style>
</style>
