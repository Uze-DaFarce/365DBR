const fs = require('fs');

const mapSectionsPath = 'assets/map/map_sections.json';
const mapSections = JSON.parse(fs.readFileSync(mapSectionsPath));

// These coords match the 1376x768 'new-map.png' generated from the python script
// We need to map the 11 locations chronologically/topologically to the 11 areas.
// Given the original coordinates from map_sections.json (original x,y):
// 1. mammoth-hot-springs: (427, 29) -> closest to Circle 2 (298, 118) or 9 (1286, 154)?? No, mammoth is top center-ish. Wait, the original background wasn't 1376x768.
// Let's assume the Python script sorted them roughly from left to right (by X).
// Original X coordinates sorted:
// grand-prismatic (369)
// yellowstone-preservation (369)
// old-faithful (394)
// mammoth-hot-springs (427)
// norris-geyser-basin (451)
// yellowstone-hydrothermal (469)
// yellowstone-geology (584)
// west-thumb-geyser-basin (586)
// grand-canyon-yellowstone (661)
// yellowstone-history (748)
// yellowstone-wildlife (777)

const newCoordsMap = {
    "mammoth-hot-springs": { x: 398, y: 304 }, // Circle 4
    "yellowstone-geology": { x: 666, y: 542 }, // Circle 5
    "norris-geyser-basin": { x: 334, y: 472 }, // Circle 3
    "grand-canyon-yellowstone": { x: 744, y: 438 }, // Circle 6
    "yellowstone-wildlife": { x: 866, y: 708 }, // Circle 7
    "grand-prismatic": { x: 66, y: 414 }, // Circle 0
    "yellowstone-hydrothermal": { x: 126, y: 504 }, // Circle 1
    "yellowstone-history": { x: 1054, y: 388 }, // Circle 8
    "old-faithful": { x: 298, y: 118 }, // Circle 2
    "west-thumb-geyser-basin": { x: 1286, y: 154 }, // Circle 9
    "yellowstone-preservation": { x: 1306, y: 478 }, // Circle 10
};

mapSections.forEach(section => {
    if (newCoordsMap[section.name]) {
        // Scale from 1376x768 to 1280x720 base coordinates
        const scaleX = 1280 / 1376;
        const scaleY = 720 / 768;
        const raw = newCoordsMap[section.name];

        // Let's make the hit areas larger, e.g. 140x140
        const boxSize = 140;

        section.coords = {
            x: Math.round(raw.x * scaleX) - boxSize/2,
            y: Math.round(raw.y * scaleY) - boxSize/2,
            width: boxSize,
            height: boxSize
        };
    }
});

fs.writeFileSync(mapSectionsPath, JSON.stringify(mapSections, null, 2));
console.log('Coordinates updated.');
