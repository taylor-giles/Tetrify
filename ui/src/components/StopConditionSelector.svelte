<script lang="ts">
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    let useTime = false,
        useAnimations = false;
    let hours = 0,
        minutes = 0,
        seconds = 0;
    let animations = 0;
    let changesMade = false;

    function onApply() {
        changesMade = false;

        //Build the stopCondition object
        let output = {
            time: useTime ? (hours * 60 + minutes) * 60 + seconds : null,
            animations: useAnimations ? animations : null,
        };

        //Dispatch output object
        dispatch("apply", output);
    }
</script>

<main>
    Stop after:
    <tr>
        <td>
            <input
                type="checkbox"
                bind:checked={useTime}
                class="checkbox-input"
                on:change={() => {
                    changesMade = true;
                }}
            />
        </td>
        <td>
            <div>
                <input
                    class="number-input"
                    type="number"
                    min="0"
                    bind:value={hours}
                    disabled={!useTime}
                    on:change={() => {
                        changesMade = true;
                    }}
                />
                h,
                <input
                    class="number-input"
                    type="number"
                    min="0"
                    bind:value={minutes}
                    disabled={!useTime}
                    on:change={() => {
                        changesMade = true;
                    }}
                />
                m,
                <input
                    class="number-input"
                    type="number"
                    min="0"
                    bind:value={seconds}
                    disabled={!useTime}
                    on:change={() => {
                        changesMade = true;
                    }}
                /> s
            </div>
        </td>
    </tr>
    <tr>
        <td>
            <input
                type="checkbox"
                bind:checked={useAnimations}
                class="checkbox-input"
                on:change={() => {
                    changesMade = true;
                }}
            />
        </td>
        <td>
            <div>
                <input
                    class="number-input"
                    type="number"
                    min="0"
                    bind:value={animations}
                    disabled={!useAnimations}
                    on:change={() => {
                        changesMade = true;
                    }}
                /> animations are found
            </div>
        </td>
    </tr>
    {#if changesMade}
        <button on:click={onApply}> Apply </button>
    {/if}
</main>

<style>
    main {
        border: 1px solid black;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .number-input {
        width: 75px;
    }
    .checkbox-input {
        margin-right: 5px;
    }
</style>
