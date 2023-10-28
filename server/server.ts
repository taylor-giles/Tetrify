import { WebSocketServer, WebSocket } from 'ws';
import { ChildProcess } from 'child_process';
import { _runEngine, _stopEngine } from '../engine/tetrifyEngine.cjs'

//Define a WebSocket wrapper type that includes a reference to child processes
type TetrifyWebSocket = WebSocket & { children: ChildProcess[] | undefined }

const TIMEOUT_MILLIS = 300000;
const PING_INTERVAL = 20000;
const PORT = parseInt(process.env.PORT ?? "6000") ?? 6000;
const wsServer = new WebSocketServer({ port: PORT });
const properties = ['grid', 'false_positives', 'false_negatives', 'enforce_gravity', 'reduce_Is']

wsServer.on('connection', (ws: TetrifyWebSocket) => {
    console.log("New connection started");

    //The only message received should be config sent to start the engine
    ws.onmessage = (event) => {
        try {
            //Parse the data
            let data = JSON.parse(event.data.toString());

            //Make sure every property was defined
            if (!properties.every((value) => value in data)) {
                throw new Error("All properties must be defined.");
            }

            //Start the engine and store reference to children
            ws.children = _runEngine(
                data["grid"],
                data["false_positives"],
                data["false_negatives"],
                data["enforce_gravity"],
                data["reduce_Is"],
                (frames) => { ws.send(JSON.stringify({ frames: frames })) },    //When an animation is found, send the frames
                () => { ws.close() },       //When simulation ends, close the websocket
                1       //Use only one thread
            );

            //After timeout, cut off the session by closing websocket
            setTimeout(() => {
                ws.close()
            }, TIMEOUT_MILLIS);

            //Setup heartbeat
            ws.on('pong', () => {
                setInterval(() => {
                    ws.ping();
                }, PING_INTERVAL);
            });
            ws.ping();
            
        } catch (error) {
            console.error("Error starting engine:\n\t", error.message);
            ws.send(Buffer.from(JSON.stringify({ log: error })));
        }
    }

    //Kill this session's child processes when its web socket is closed
    ws.onclose = (event) => {
        console.log("Connection closed")
        if (ws.children) {
            ws.children.forEach((child) => child.kill())
        }
    }
});

// When server closes, stop *all* children (across all sessions)
wsServer.on('close', () => {
    console.log("Server closed.");
    _stopEngine();
});

wsServer.on("listening", () => {
    console.log(`Websocket server listening on port ${PORT}`)
});

