<script lang="ts">
    import { getNumCores } from "../../../engine/runEngine.cjs";

    export let isRunning: boolean;
    export let falsePositives: number;
    export let falseNegatives: number;
    export let enforceGravity: boolean;
    export let numThreads: number;
    export let removeDuplicates: boolean;
    export let colors: object;
    export let height: number;
    export let width: number;
    export let backgroundColor: string;
    export let borderColor: string;
    export let borderThickness: number;
    export let cellSize: number;
    export let animationSpeed: number;

    // Make sure option values stay defined & positive
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
</script>

<div id="options-container">
    <div class="region-header">Options</div>
    <div class="section-header">Simulation Options</div>
    {#if isRunning}
        <div>(Disabled while simulation is running)</div>
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
                    disabled={isRunning}
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
                    disabled={isRunning}
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
                    disabled={isRunning}
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
                    disabled={isRunning}
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
                    disabled={isRunning}
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
                <div class="option-label">Canvas Height:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="1"
                    bind:value={height}
                    class="number-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Canvas Width:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="4"
                    bind:value={width}
                    class="number-input"
                />
            </td>
        </tr>
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
                <div class="option-label">Border Thickness:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    bind:value={borderThickness}
                    class="number-input"
                />
            </td>
        </tr>
        <tr>
            <td>
                <div class="option-label">Cell Size:</div>
            </td>
            <td>
                <input
                    type="number"
                    min="0"
                    bind:value={cellSize}
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
                    min="0"
                    bind:value={animationSpeed}
                    class="number-input"
                />
            </td>
        </tr>
    </table>
</div>

<style>
    #options-container {
        height: 90vh;
        width: 300px;
        padding: 20px;
        border: 2px solid black;
        border-radius: 20px;
        white-space: nowrap;
        overflow-y: auto;
        scrollbar-width: thin;
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
