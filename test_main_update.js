const fs = require('fs');
const code = fs.readFileSync('apps/HeIsRisen/main.js', 'utf8');

// Find all update() functions
const regex = /update\(\) \{([\s\S]*?)\n  \}/g;
let match;
while ((match = regex.exec(code)) !== null) {
    console.log("---- match ----");
    console.log(match[0]);
}
