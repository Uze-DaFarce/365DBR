const fs = require('fs');

let content = fs.readFileSync('index.html', 'utf8');

const search = `  const [currentDate, setCurrentDate] = useState(initialState.date);`;

const replace = `  const [currentDate, setCurrentDate] = useState(() => {
      const params = new URLSearchParams(window.location.search);
      const d = params.get('d');
      return d || initialState.date;
  });`;

if (content.includes(search)) {
    content = content.replace(search, replace);
    fs.writeFileSync('index.html', content);
    console.log("Replaced successfully!");
} else {
    console.log("Could not find search block.");
}
