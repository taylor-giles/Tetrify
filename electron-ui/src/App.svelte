<script lang="ts">
  import ToggleGrid from './components/ToggleGrid.svelte';

  let grid = [];
  let target = "";
</script>

<main>
  <div>
  </div>

  <ToggleGrid 
    width={20}
    height={20}
    bind:grid>
  </ToggleGrid>
</main>

<style>
</style>
