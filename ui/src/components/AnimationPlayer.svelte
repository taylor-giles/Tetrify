<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import {
    makeAndSaveGif,
    generateImageURL,
    saveImageFromURL,
  } from "../tetrifyImageUtils";
  import ColorGrid from "./ColorGrid.svelte";
  const dispatch = createEventDispatcher();

  const MILLIS_TO_HANG = 1000;

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

  export let hangAtEnd: boolean;
  let displayFrames = [];

  let animationInterval: any;
  let mainView: any; //Reference to ColorGrid (gets bound later)

  //Apply new frameDelay whenever it changes by re-creating the interval (restart)
  $: {
    frameDelay;
    restart();
  }

  //Start from frame 0 (reset) whenever the animation itself changes
  $: {
    displayFrames = frames ? [...frames] : [];
    reset();
  }

  //Handle toggling of hanging on last frame
  $: handleHangAtEnd(hangAtEnd);
  function handleHangAtEnd(doHang: boolean){
    displayFrames = frames ? [...frames] : [];
    if (doHang && frames) {
      let lastFrame = frames[frames.length - 1];
      let numTimesToRepeat = parseInt(`${MILLIS_TO_HANG / frameDelay}`)
      for (let i = 0; i < numTimesToRepeat; i++) {
        displayFrames.push(lastFrame);
      }
    }

    //Go back to beginning if hangAtEnd was toggled during the hang period
    if(frames && frameIndex > frames.length){
      frameIndex = 0;
    }
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
    handleHangAtEnd(hangAtEnd);
    resume();
  }

  export function resume() {
    animationInterval = setInterval(async () => {
      if (displayFrames && displayFrames.length) {
        //Display the current frame
        displayFrame(displayFrames[frameIndex]);

        // //Hang on last frame (if needed)
        // if(frameIndex == displayFrames.length-1 && hangAtEnd){
        //   await new Promise(res => setTimeout(res, 1000));
        // }

        //Move to the next frame
        frameIndex = (frameIndex + 1) % displayFrames.length;
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
    for (let frame of displayFrames) {
      frameURLs.push(
        await generateImageURL(
          computeColorGrid(frame),
          borderColor,
          borderThickness,
          cellHeight,
          cellWidth
        )
      );
      dispatch(
        "gifProgressUpdate",
        `Generating: ${((displayFrames.indexOf(frame) / displayFrames.length) * 100).toFixed(
          0
        )}%`
      );
    }

    //Save the gif (or image, if there is only one frame)
    if (frameURLs.length > 1) {
      makeAndSaveGif(frameURLs, frameDelay, (update) => {
        dispatch("gifProgressUpdate", update);
      });
    } else {
      dispatch("gifProgressUpdate", null);
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
