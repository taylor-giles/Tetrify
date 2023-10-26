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
  export let disabled = false;
  let dragType = false; //Used to prevent dragging from always toggling every cell it touches

  // Make the grid of booleans to represent the cells
  export let grid = [];

  $: {
    width; height;
    defineGrid();
  }

  export function defineGrid(){
    grid = []
    for (let i = 0; i < height; i++) {
      let row = [];
      for (let j = 0; j < width; j++) {
        row.push(false);
      }
      grid.push(row);
    }
    grid = grid;
  }

  export function invertGrid() {
    for (let i = 0; i < height; i++) {
      for (let j = 0; j < width; j++) {
        grid[i][j] = !grid[i][j];
      }
    }
    grid = grid;
  }

  function onStartDrag(e){
    dragType = e.detail;
  }

</script>

<div>
  {#each grid as row}
    <div class="row" style="--height: calc({cellHeight} + {cellMargin} * 2)">
      {#each row as cell}
        <ToggleCell
          width={cellWidth}
          height={cellHeight}
          border={cellBorder}
          margin={cellMargin}
          {onColor}
          {offColor}
          allowDrag={allowDrag && dragType !== cell}
          {disabled}
          bind:isToggled={cell}
          on:startDrag={onStartDrag}
        />
      {/each}
    </div>
  {/each}
</div>

<style>
  .row {
    padding: 0px;
    margin: 0px;
    height: var(--height);
    white-space: nowrap;
    line-height: 1;
  }
</style>
