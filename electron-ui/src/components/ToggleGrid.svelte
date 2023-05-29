<script lang="ts">
  import ToggleCell from "./ToggleCell.svelte";

  export let width: number, height: number;
  export let cellWidth = "20px",
    cellHeight = "20px",
    cellBorder = "1px solid black",
    cellMargin = "0px";
  export let onColor = "#ffffff",
    offColor = "#000000";
  export let allowDrag = true;

  // Make the grid of booleans to represent the cells
  export let grid = [];
  for (let i = 0; i < height; i++) {
    let row = [];
    for (let j = 0; j < width; j++) {
      row.push(false);
    }
    grid.push(row);
  }
</script>

<div>
  {#each grid as row}
    <div class="row" style="--height: calc({cellHeight} + {cellMargin} * 2)">
      {#each row as cell}
        <ToggleCell
          bind:width={cellWidth}
          bind:height={cellHeight}
          bind:border={cellBorder}
          bind:margin={cellMargin}
          bind:onColor
          bind:offColor
          bind:allowDrag
          bind:isToggled={cell}
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
