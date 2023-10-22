import { createCanvas, Canvas } from "canvas";
import GIF from 'gif.js';

// Function to convert a hexadecimal color string to an RGB array
function hexToRgb(hex: string): [number, number, number] {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
        ? [
            parseInt(result[1], 16),
            parseInt(result[2], 16),
            parseInt(result[3], 16),
        ]
        : [0, 0, 0];
}

/**
 * Generates an image for a given array of hex color values, with borders around each cell
 */
export async function generateImageURL(frame: string[][], borderColor: string, borderSize: number, cellHeight: number, cellWidth: number): Promise<string> {
    const fullCellWidth = (cellWidth + (2 * borderSize));
    const fullCellHeight = (cellHeight + (2 * borderSize));
    const width = frame[0].length * fullCellWidth;
    const height = frame.length * fullCellHeight;
    const canvas: Canvas = createCanvas(width, height);
    const ctx = canvas.getContext("2d");

    //Compute the border color once, to avoid repeating computation
    const [borderR, borderG, borderB] = hexToRgb(borderColor)
    const borderFillStyle = `rgb(${borderR}, ${borderG}, ${borderB})`;

    //Draw the frame onto the canvas
    for (let row = 0; row < frame.length; row++) {
        for (let col = 0; col < frame[row].length; col++) {
            //Draw the border as a background
            ctx.fillStyle = borderFillStyle;
            ctx.fillRect(col * fullCellWidth, row * fullCellHeight, fullCellWidth, fullCellHeight);

            //Draw the cell on top of the "border"
            let [r, g, b] = hexToRgb(frame[row][col])
            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.fillRect(col * fullCellWidth + borderSize, row * fullCellHeight + borderSize, fullCellWidth - 2 * borderSize, fullCellHeight - 2 * borderSize);
        }
    }
    return canvas.toDataURL();
}

/**
 * Downloads the image from the provided URL string
 * @param imageURL The URL of the image to download
 */
export async function saveImageFromURL(imageURL: string){
    //Create anchor element for link
    let link = document.createElement('a');
    link.href = imageURL;
    link.download = 'tetrify.png';

    //Do the download
    link.click();
}


/**
 * Compiles the provided frames into a gif and downloads that gif
 * @param frameURLs List of image URLs for the frames
 * @param delay The delay in millis between each frame
 * @param onProgressUpdate Callback used to pass a progress string back to the caller whenever an update is made. Passes null when process is finished.
 */
export async function makeAndSaveGif(frameURLs: string[], delay: number, onProgressUpdate: (update: string | null)=>void) {
    let gif = new GIF({
        workers: 8,
        quality: 10
    });

    gif.on('finished', (blob) => {
        //Generate URL for blob object
        let url = URL.createObjectURL(blob);

        //Create "anchor element" for link
        const link = document.createElement("a");

        //Generate link URL
        link.href = url;
        link.download = "tetrify.gif";

        //Do the download
        link.click();

        //Revoke the URL
        URL.revokeObjectURL(url);

        //Send empty progress update
        onProgressUpdate(null)
    });

    gif.on('progress', (percent) => {
        onProgressUpdate(`Rendering: ${(percent*100).toFixed(0)}%`)
    })

    //Add the frames to the gif
    for (let frameURL of frameURLs) {
        let img = new Image();
        img.src = frameURL;
        await elementLoaded(img);
        gif.addFrame(img, { delay: delay });
    }

    //Render the gif
    gif.render();
}

// Function to wait for an element to load
async function elementLoaded(element: HTMLElement): Promise<void> {
    return new Promise((resolve) => {
        element.onload = () => resolve();
    });
}

