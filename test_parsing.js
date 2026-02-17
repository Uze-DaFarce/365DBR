const fs = require('fs');

const BOOK_NAMES = {
  GEN: 'Genesis', EXO: 'Exodus', LEV: 'Leviticus', NUM: 'Numbers', DEU: 'Deuteronomy', JOS: 'Joshua', JDG: 'Judges', RUT: 'Ruth', '1SA': '1 Samuel', '2SA': '2 Samuel', '1KI': '1 Kings', '2KI': '2 Kings', '1CH': '1 Chronicles', '2CH': '2 Chronicles', EZR: 'Ezra', NEH: 'Nehemiah', EST: 'Esther', JOB: 'Job', PSA: 'Psalms', PRO: 'Proverbs', ECC: 'Ecclesiastes', SON: 'Song of Solomon', ISA: 'Isaiah', JER: 'Jeremiah', LAM: 'Lamentations', EZK: 'Ezekiel', DAN: 'Daniel', HOS: 'Hosea', JOE: 'Joel', AMO: 'Amos', OBA: 'Obadiah', JON: 'Jonah', MIC: 'Micah', NAH: 'Nahum', HAB: 'Habakkuk', ZEP: 'Zephaniah', HAG: 'Haggai', ZEC: 'Zechariah', MAL: 'Malachi',
  MAT: 'Matthew', MRK: 'Mark', LUK: 'Luke', JHN: 'John', ACT: 'Acts', ROM: 'Romans', '1CO': '1 Corinthians', '2CO': '2 Corinthians', GAL: 'Galatians', EPH: 'Ephesians', PHP: 'Philippians', COL: 'Colossians', '1TH': '1 Thessalonians', '2TH': '2 Thessalonians', '1TI': '1 Timothy', '2TI': '2 Timothy', TIT: 'Titus', PHM: 'Philemon', HEB: 'Hebrews', JAS: 'James', '1PE': '1 Peter', '2PE': '2 Peter', '1JN': '1 John', '2JN': '2 John', '3JN': '3 John', JUD: 'Jude', REV: 'Revelation'
};

const BIBLE_BOOK_ORDER = Object.keys(BOOK_NAMES);
const BIBLE_BOOK_ORDER_MAP = new Map(BIBLE_BOOK_ORDER.map((b, i) => [b, i]));

const readings = JSON.parse(fs.readFileSync('readings.json', 'utf8'));

const newIndex = {};
const books = new Set();

readings.forEach(day => {
    if (!day.api_format) return;
    const ranges = day.api_format.split(',');
    ranges.forEach(range => {
        const subRanges = range.split(';');
        subRanges.forEach(part => {
            // GEN.1.1-GEN.1.31
            const [start, end] = part.split('-');
            const [sBook, sCh] = start.split('.');
            const [eBook, eCh] = end.split('.');

            const sBookIdx = BIBLE_BOOK_ORDER_MAP.get(sBook);
            const eBookIdx = BIBLE_BOOK_ORDER_MAP.get(eBook);

            if (sBookIdx === undefined || eBookIdx === undefined) {
                console.log(`Missing book: ${sBook} or ${eBook}`);
                return;
            }

            // Iterate Books
            for (let bIdx = sBookIdx; bIdx <= eBookIdx; bIdx++) {
                const book = BIBLE_BOOK_ORDER[bIdx];
                books.add(book);
            }
        });
    });
});

console.log('Books found:', Array.from(books));
