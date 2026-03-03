const fs = require('fs');

let content = fs.readFileSync('bible.html', 'utf8');

const search = `            // Map known discrepancies between standard 3-letter codes and the raw USFM/OSIS data codes
            const BOOK_MAP = {
                'SON': 'SNG', // Song of Solomon
                'JOE': 'JOL', // Joel
                'NAH': 'NAM'  // Nahum
            };
            const dataBook = BOOK_MAP[selectedBook] || selectedBook;
            const prefix = \`\${dataBook}.\${selectedChapter}.\`;
            const filteredVids = Object.keys(mergedMap).filter(vid => vid.startsWith(prefix));

            if (filteredVids.length === 0) throw new Error("Chapter content missing from data.");

            // Sort
            filteredVids.sort((a,b) => {
               const vA = parseInt(a.split('.')[2]);
               const vB = parseInt(b.split('.')[2]);
               return vA - vB;
            });

            // Map the matched keys back to the standard selectedBook code (e.g. SNG -> SON)
            // This ensures all downstream consumers like targetScrollVerse which use 'SON' work perfectly.
            const normalizedFilteredVids = filteredVids.map(vid => vid.replace(\`\${dataBook}.\`, \`\${selectedBook}.\`));

            const finalMap = {};
            filteredVids.forEach((vid, i) => {
                const normalizedVid = normalizedFilteredVids[i];
                finalMap[normalizedVid] = mergedMap[vid];
            });

            setVerseMap(finalMap);
            setSortedVids(normalizedFilteredVids);
            setAvailableTranslations(Array.from(keys));`;

const replace = `            // Filter for Selected Chapter (Strict Prefix Match: "GEN.1.")
            // Note: Use dot to avoid "GEN.11" matching "GEN.1" prefix logic if naive.
            const prefix = \`\${selectedBook}.\${selectedChapter}.\`;
            const filteredVids = Object.keys(mergedMap).filter(vid => vid.startsWith(prefix));

            if (filteredVids.length === 0) throw new Error("Chapter content missing from data.");

            // Sort
            filteredVids.sort((a,b) => {
               const vA = parseInt(a.split('.')[2]);
               const vB = parseInt(b.split('.')[2]);
               return vA - vB;
            });

            const finalMap = {};
            filteredVids.forEach(vid => finalMap[vid] = mergedMap[vid]);

            setVerseMap(finalMap);
            setSortedVids(filteredVids);
            setAvailableTranslations(Array.from(keys));`;

if (content.includes(search)) {
    content = content.replace(search, replace);
    fs.writeFileSync('bible.html', content);
    console.log("Replaced successfully!");
} else {
    console.log("Could not find search block.");
}
