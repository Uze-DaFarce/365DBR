const fs = require('fs');

let content = fs.readFileSync('index.html', 'utf8');
const search = `const BIBLE_BOOK_ORDER_MAP = new Map(BIBLE_BOOK_ORDER.map((b, i) => [b, i]));`;

console.log(content.substring(content.indexOf('BIBLE_BOOK_ORDER_MAP')-200, content.indexOf('BIBLE_BOOK_ORDER_MAP')+100));
