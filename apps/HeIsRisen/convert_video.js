const ffmpeg = require('fluent-ffmpeg');
const ffmpegPath = require('ffmpeg-static');

// Set the path to the ffmpeg binary
ffmpeg.setFfmpegPath(ffmpegPath);

// Replace with the path to your source .mov file
const inputPath = 'D:\\Users\\uzeda\\Documents\\Adobe\\Premiere Pro\\26.0\\level-complete.mov';
// Replace with where you want the .webm saved
const outputPath = 'assets\\video\\level-complete.webm';

console.log('Starting conversion... This might take a minute or two depending on your CPU.');

ffmpeg(inputPath)
    .videoCodec('libvpx-vp9')
    .outputOptions([
        '-pix_fmt yuva420p', // Ensure alpha channel is preserved
        '-auto-alt-ref 0',   // Required for alpha in WebM
        '-b:v 2M'            // Target bitrate
    ])
    .on('end', () => {
        console.log('Conversion finished successfully! You can find your transparent WebM at:', outputPath);
    })
    .on('error', (err) => {
        console.error('An error occurred during conversion:', err.message);
    })
    .save(outputPath);
