const fs = require('fs');
const code = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');

const regex = /update\(\) \{([\s\S]*?)\n  \}/g;
let match;
while ((match = regex.exec(code)) !== null) {
    console.log("---- match ----");
    console.log(match[0]);
}
