<script lang="ts">
    export let width = "20px",
        height = "20px",
        margin = "0px";
    export let border = "1px solid black";
    export let color = "#000000";
</script>

<button
    id="main"
    style="--height: {height}; --width: {width}; --margin: {margin}; --color: {color}; --border: {border};"
/>

<style>
    #main {
        width: var(--width);
        height: var(--height);
        background-color: var(--color);
        border: var(--border);
        margin: var(--margin);
        border-radius: 0;
        padding: 0;
    }
</style>
