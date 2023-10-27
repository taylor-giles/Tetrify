//Load the engine functions
const ENGINE_FUNCTIONS = require('../engine/tetrifyEngine.cjs');
process.once('loaded', () => {
    global.ENGINE_FUNCTIONS = ENGINE_FUNCTIONS
})