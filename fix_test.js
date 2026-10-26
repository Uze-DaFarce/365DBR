const fs = require('fs');
let testCode = fs.readFileSync('apps/HeIsRisen/tests/test_state_corruption.js', 'utf8');

// I will rewrite the test_state_corruption.js to use standard Playwright execution
