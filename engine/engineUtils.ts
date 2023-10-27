//True iff the app is running in electron window
export const IS_ELECTRON = navigator.userAgent.toLowerCase().indexOf(" electron/") > -1;

//Websocket object reference (only used when running engine via RPC)
let webSocket: WebSocket;

/**
 * Uses a websocket to run the engine on a remote server via RPC.
 * Returns a reference to the websocket object
 */
function runEngineRemote(
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
    webSocket = new WebSocket("wss://tetrify.taylorgiles.me/wss");

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
function stopEngineRemote() {
    webSocket.close();
}

// Define runEngine, stopEngine, and getNumCores according to the context the app is running in.
// If running in electron, then define engine functions to interface with engine directly. Otherwise, use remote definitions.
// NOTE: The global.ENGINE_FUNCTIONS are references to the functions in tetrifyEngine. 
// They are loaded in the Electron preload script and added to the global reference scope for access here.
const REMOTE_FUNCTIONS = { _runEngine: runEngineRemote, _stopEngine: stopEngineRemote, _getNumCores: () => 1 }
const CHOSEN_FUNCTIONS = IS_ELECTRON && global.ENGINE_FUNCTIONS ? global.ENGINE_FUNCTIONS : REMOTE_FUNCTIONS

export function runEngine(grid,
    falsePositives: number,
    falseNegatives: number,
    enforceGravity: boolean,
    reduceWellsAndTowers: boolean,
    onSuccess: (frames: string[][]) => any,
    onEnd: () => any,
    numThreads: number) {
    return CHOSEN_FUNCTIONS._runEngine(grid,
        falsePositives,
        falseNegatives,
        enforceGravity,
        reduceWellsAndTowers,
        onSuccess,
        onEnd,
        numThreads)

}

export function stopEngine() {
    return CHOSEN_FUNCTIONS._stopEngine();
}

export function getNumCores() {
    return CHOSEN_FUNCTIONS._getNumCores();
}

