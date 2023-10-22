<script lang="ts">
    import { getNumCores } from "../../../engine/runEngine.cjs";
    import {
        AppContextMode,
        MAX_HEIGHT,
        MAX_WIDTH,
        MIN_HEIGHT,
        MIN_WIDTH,
    } from "../App.svelte";

    export let currentMode: AppContextMode;
    export let falsePositives: number;
    export let falseNegatives: number;
    export let enforceGravity: boolean;
    export let numThreads: number;
    export let removeDuplicates: boolean;
    export let reduceWellsAndTowers: boolean;
    export let colors: object;
    export let height: number;
    export let width: number;
    export let backgroundColor: string;
    export let borderColor: string;
    export let borderThickness: number;
    export let cellWidth: number;
    export let cellHeight: number;
    export let animationSpeed: number;

    // Make sure option values stay defined and within range
    $: if (!falsePositives || falsePositives < 0) {
        falsePositives = 0;
    }
    $: if (!falseNegatives || falseNegatives < 0) {
        falseNegatives = 0;
    }

    $: if (!numThreads || numThreads < 1) {
        numThreads = 1;
    }
    $: if (numThreads > getNumCores()) {
        numThreads = getNumCores();
    }

    $: if (!height || height < MIN_HEIGHT) {
        height = MIN_HEIGHT;
    }
    $: if (height > MAX_HEIGHT) {
        height = MAX_HEIGHT;
    }

    $: if (!width || width < MIN_WIDTH) {
        width = MIN_WIDTH;
    }
    $: if (width > MAX_WIDTH) {
        width = MAX_WIDTH;
    }

    $: if (!cellWidth || cellWidth < 0) {
        cellWidth = 0;
    }
    $: if (!cellHeight || cellHeight < 0) {
        cellHeight = 0;
    }

    $: if (!borderThickness || borderThickness < 0) {
        borderThickness = 0;
    }
    $: if (borderThickness > Math.min(cellHeight, cellWidth) / 2) {
        borderThickness = Math.min(cellHeight, cellWidth) / 2;
    }
    $: if(animationSpeed > 100){
        animationSpeed = 100;
    }
</script>

<div id="options-container">
    <div class="region-header">Options</div>
    <div class="section-header">Canvas Options</div>
    {#if currentMode != AppContextMode.DRAWING}
        <div>(Locked outside edit mode)</div>
    {/if}
    <table>
        <tr>
            <td>
                <div class="option-label">Canvas Height (cells):</div>
            </td>
            <td>
                <input
                    type="number"
                    min={MIN_HEIGHT}
                    max={MAX_HEIGHT}
                    bind:value={height}
                    disabled={currentMode != AppContextMode.DRAWING}
                    class="number-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Canvas Width (cells):</div>
            </td>
            <td>
                <input
                    type="number"
                    min={MIN_WIDTH}
                    max={MAX_WIDTH}
                    bind:value={width}
                    disabled={currentMode != AppContextMode.DRAWING}
                    class="number-input"
                />
            </td>
        </tr>
    </table>
    <div class="section-header">Simulation Options</div>
    {#if currentMode == AppContextMode.RUNNING}
        <div>(Locked while simulation is running)</div>
    {/if}
    <table>
        <tr>
            <td>
                <div class="option-label">False Positives:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    bind:value={falsePositives}
                    class="number-input"
                    title="Hi there"
                    disabled={currentMode == AppContextMode.RUNNING}
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">False Negatives:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    bind:value={falseNegatives}
                    class="number-input"
                    disabled={currentMode == AppContextMode.RUNNING}
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Enforce Gravity:</div>
            </td>
            <td>
                <input
                    type="checkbox"
                    bind:checked={enforceGravity}
                    class="checkbox-input"
                    disabled={currentMode == AppContextMode.RUNNING}
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Reduce Wells & Towers:</div>
            </td>
            <td>
                <input
                    type="checkbox"
                    bind:checked={reduceWellsAndTowers}
                    class="checkbox-input"
                    disabled={currentMode == AppContextMode.RUNNING}
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Number of Threads:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="1"
                    max={getNumCores()}
                    bind:value={numThreads}
                    class="number-input"
                    disabled={currentMode == AppContextMode.RUNNING}
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Remove Duplicates:</div>
            </td>
            <td>
                <input
                    type="checkbox"
                    bind:checked={removeDuplicates}
                    class="checkbox-input"
                    disabled={currentMode == AppContextMode.RUNNING}
                />
            </td>
        </tr>
    </table>

    <div class="section-header">Block Colors</div>
    <table>
        {#each Object.keys(colors) as blockName}
            <tr>
                <td>
                    <div class="color-label">
                        "{blockName}" Block:
                    </div>
                </td>
                <td>
                    <input
                        type="color"
                        bind:value={colors[blockName]}
                        class="color-input"
                    />
                </td>
            </tr>
        {/each}
    </table>

    <div class="section-header">Display Options</div>
    <table>
        <tr>
            <td>
                <div class="option-label">Background Color:</div>
            </td>
            <td>
                <input
                    type="color"
                    bind:value={backgroundColor}
                    class="color-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Border Color:</div>
            </td>
            <td>
                <input
                    type="color"
                    bind:value={borderColor}
                    class="color-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Border Thickness (px):</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    max={Math.min(cellHeight, cellWidth) / 2}
                    bind:value={borderThickness}
                    class="number-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Cell Width (px):</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    bind:value={cellWidth}
                    class="number-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Cell Height (px):</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    bind:value={cellHeight}
                    class="number-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Animation Speed:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="1"
                    step="1"
                    max="100"
                    bind:value={animationSpeed}
                    class="number-input"
                />
            </td>
        </tr>
    </table>
</div>

<style>
    #options-container {
        height: 100%;
        width: max-content;
        padding: 20px;
        border: 2px solid black;
        border-radius: 20px;
        overflow-y: auto;
        scrollbar-width: thin;
        box-sizing: border-box;
    }

    td {
        padding-bottom: 10px;
        padding-inline: 5px;
    }
    table {
        margin-bottom: 20px;
    }
    .number-input {
        width: 100px;
        margin: 0px;
    }
    .option-label {
        height: 100%;
    }
    .color-label {
        font-family: "Courier New", Courier, monospace;
        margin-left: 5px;
    }
    .region-header {
        font-weight: bold;
        font-size: 28px;
        text-align: center;
        width: 100%;
        margin-bottom: 10px;
    }
    .section-header {
        font-weight: bold;
        font-size: 20px;
    }
    .color-input {
        border: 1px;
        margin: 0px 0px 0px 15px;
        padding: 0;
        width: 100px;
        cursor: pointer;
    }
</style>
