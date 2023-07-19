<script lang="ts">
    export let width = "20px",
        height = "20px",
        margin = "0px";
    export let border = "1px solid black";
    export let onColor = "#ffffff",
        offColor = "#000000";
    export let allowDrag = true;
    export let isToggled = false;
    export let disabled = false;
    let currentColor = offColor;

    $: currentColor = isToggled ? onColor : offColor;

    function toggle() {
        if(!disabled){
            isToggled = !isToggled;
        }
    }

    function onMouseOver(e) {
        if (allowDrag && e.buttons === 1) {
            toggle();
        }
    }
</script>

<button
    id="main"
    style="--height: {height}; --width: {width}; --margin: {margin}; --color: {currentColor}; --border: {border};"
    on:mousedown={toggle}
    on:mouseover={onMouseOver}
    on:focus={() => {}}
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
