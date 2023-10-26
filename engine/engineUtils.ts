//True iff the app is running in electron window
export const IS_ELECTRON = navigator.userAgent.toLowerCase().indexOf(" electron/") > -1;

//Websocket object reference (only used when running engine via RPC)
let webSocket: WebSocket;

/**
 * Uses a websocket to run the engine on a remote server via RPC.
 * Returns a reference to the websocket object
 */
export function runEngineRemote(
    grid,
    falsePositives,
    falseNegatives,
    enforceGravity,
    reduceWellsAndTowers,
    onSuccess,
    onEnd,
    numThreads
) {
    //Use websocket to start engine
    webSocket = new WebSocket("ws://localhost:6000");

    webSocket.addEventListener("open", (event) => {
        //Build config object
        let engineConfig = {
            grid: grid,
            false_positives: falsePositives,
            false_negatives: falseNegatives,
            enforce_gravity: enforceGravity,
            reduce_Is: reduceWellsAndTowers,
        };

        //Send data to server
        webSocket.send(JSON.stringify(engineConfig))
    });


    /**
     * React to messages from server (log and frames)
     */
    webSocket.addEventListener('message', (event) => {
        try {
            let data = JSON.parse(event.data);
            //Log messages
            if ("log" in data) {
                console.log(`[LOG] ${data.log}`)
            }

            //Frames (animation finding was successful)
            if ("frames" in data) {
                onSuccess(data.frames)
            }
        } catch (e) {
            console.error(`Error parsing message from server: ${event.data}`, e)
        }
    });

    //React to websocket closing (the engine has stopped)
    webSocket.addEventListener("close", (event) => {
        onEnd();
    });
}


/**
 * Close the websocket (it is up to the server to stop the engine)
 */
export function stopEngineRemote() {
    webSocket.close();
}

// Define runEngine, stopEngine, and getNumCores according to the context the app is running in.
// If running in electron, then define engine functions to interface with engine directly. Otherwise, use remote definitions.
const REMOTE_FUNCTIONS = { runEngine: runEngineRemote, stopEngine: stopEngineRemote, getNumCores: () => 1 }
let chosenFunctions = REMOTE_FUNCTIONS
if (IS_ELECTRON) {
    import("./tetrifyEngine.cjs").then(
        ({ _runEngine, _stopEngine, _getNumCores }) => {
            console.log("Using local engine");
            chosenFunctions = { runEngine: _runEngine, stopEngine: _stopEngine, getNumCores: _getNumCores };
        }
    )
        .catch((error) => {
            //On failure to import, default to remote functions
            console.error(`Error importing engine. Defaulting to RPC engine.`, error);
            chosenFunctions = REMOTE_FUNCTIONS;
        });
}

export function runEngine(grid,
    falsePositives,
    falseNegatives,
    enforceGravity,
    reduceWellsAndTowers,
    onSuccess,
    onEnd,
    numThreads) {
    return chosenFunctions.runEngine(grid,
        falsePositives,
        falseNegatives,
        enforceGravity,
        reduceWellsAndTowers,
        onSuccess,
        onEnd,
        numThreads)

}

export function stopEngine() {
    return chosenFunctions.stopEngine();
}

export function getNumCores() {
    return chosenFunctions.getNumCores();
}

