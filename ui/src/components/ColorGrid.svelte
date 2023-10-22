<script lang="ts">
  import ColorCell from "./ColorCell.svelte";
  import { generateImageURL } from "../tetrifyImageUtils";

  export let width: number, height: number;
  export let cellWidth = 20,
    cellHeight = 20,
    cellBorderThickness = 1,
    cellBorderColor = "#000000",
    cellMargin = "0px";
  export let defaultColor = "#000000";

  // Make the grid of colors to represent the cells
  export let grid = [];

  let mainView; //Reference to the main div of this component (gets bound later)

  $: {
    width;
    height;
    defaultColor;
    defineGrid();
  }

  function defineGrid() {
    grid = [];
    for (let i = 0; i < height; i++) {
      let row = [];
      for (let j = 0; j < width; j++) {
        row.push(defaultColor);
      }
      grid.push(row);
    }
    grid = grid;
  }

  export async function saveAsImage(filename) {
    let url = await generateImageURL(
      grid,
      cellBorderColor,
      cellBorderThickness,
      cellHeight,
      cellWidth
    );

    //Create "anchor element" for link
    const link = document.createElement("a");
    link.href = url;
    
    //Do the download
    link.download = filename;
    link.click();
  }
</script>

<div bind:this={mainView}>
  {#each grid as row}
    <div class="row" style="--height: calc({cellHeight}px + {cellMargin} * 2)">
      {#each row as cell}
        <ColorCell
          width={`${cellWidth}px`}
          height={`${cellHeight}px`}
          border={`${cellBorderThickness}px solid ${cellBorderColor}`}
          margin={cellMargin}
          color={cell}
        />
      {/each}
    </div>
  {/each}
</div>

<style>
  .row {
    padding: 0;
    margin: 0;
    height: var(--height);
    white-space: nowrap;
  }
</style>
