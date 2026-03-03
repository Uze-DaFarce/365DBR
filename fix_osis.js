const fs = require('fs');

function updateFile(file) {
    let content = fs.readFileSync(file, 'utf8');

    // BOOK_NAMES update
    content = content.replace(/'SON': 'Song of Solomon'/g, "'SNG': 'Song of Solomon'");
    content = content.replace(/SON: 'Song of Solomon'/g, "SNG: 'Song of Solomon'"); // handle unquoted
    content = content.replace(/'JOE': 'Joel'/g, "'JOL': 'Joel'");
    content = content.replace(/JOE: 'Joel'/g, "JOL: 'Joel'");
    content = content.replace(/'NAH': 'Nahum'/g, "'NAM': 'Nahum'");
    content = content.replace(/NAH: 'Nahum'/g, "NAM: 'Nahum'");

    // BIBLE_BOOK_ORDER update
    content = content.replace(/"SON"/g, '"SNG"');
    content = content.replace(/"JOE"/g, '"JOL"');
    content = content.replace(/"NAH"/g, '"NAM"');

    // VERSE_COUNTS update
    content = content.replace(/"SON": \[/g, '"SNG": [');
    content = content.replace(/"JOE": \[/g, '"JOL": [');
    content = content.replace(/"NAH": \[/g, '"NAM": [');

    fs.writeFileSync(file, content);
    console.log(`Updated ${file}`);
}

updateFile('bible.html');
updateFile('index.html');
