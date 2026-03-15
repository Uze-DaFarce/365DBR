const fs = require('fs');
const c = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');
const eggZam = c.indexOf("class EggZamRoom");
const start = c.indexOf("this.currentEgg = null;", eggZam);
const end = c.indexOf("window.location.reload();", start);
// find the closing brace of the if block
const closing = c.indexOf("}", end + 30) + 1; // It usually takes one or two `}` to close out. Let's just print a chunk
console.log(c.substring(start, closing + 50));
