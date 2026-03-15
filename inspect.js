const fs = require('fs');
const c = fs.readFileSync('apps/HeIsRisen/m/main.js', 'utf8');
const eggZam = c.indexOf("class EggZamRoom");
const start = c.indexOf("this.currentEgg = null;", eggZam);
const end = c.indexOf("return;", start) + 7;
console.log(c.substring(start, end + 20)); // print a bit past the return to see what's there
