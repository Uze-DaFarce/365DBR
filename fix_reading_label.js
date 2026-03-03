const fs = require('fs');

let content = fs.readFileSync('index.html', 'utf8');

const search = `  // Derived state to replace duplicate parsing in Header and Main App
  // Re-runs only when the underlying raw data (verseMap/sortedVids) changes.
  const readingLabel = useMemo(() => {
      if (!verseMap || sortedVids.length === 0) return '';
      const firstVid = sortedVids[0];
      const lastVid = sortedVids[sortedVids.length - 1];
      if (!firstVid || !lastVid) return '';

      const s = firstVid.split('.');
      const e = lastVid.split('.');
      if (s.length < 3 || e.length < 3) return '';`;

const replace = `  // Derived state to replace duplicate parsing in Header and Main App
  // Re-runs only when the underlying raw data (verseMap/sortedVids) changes.
  const readingLabel = useMemo(() => {
      if (!verseMap || sortedVids.length === 0) return '';
      const firstVid = sortedVids[0];
      const lastVid = sortedVids[sortedVids.length - 1];
      if (!firstVid || !lastVid) return '';

      const s = firstVid.split('.');
      const e = lastVid.split('.');
      if (s.length < 3 || e.length < 3) return '';`;


if (content.includes(search)) {
    content = content.replace(search, replace);
    fs.writeFileSync('index.html', content);
    console.log("Replaced successfully!");
} else {
    console.log("Could not find search block.");
}
