// A clean script that imports the source file as text, and evaluates ONLY what we need
// to verify state corruption without messy regex extraction or evaluating entire files that break on context.
// We will test the initializeGameData by actually evaluating it inside an empty context.

const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Navigate to an actual local domain so localStorage APIs do not throw security errors
  await page.goto('http://127.0.0.1:8080').catch(() => {});

  const mainCode = fs.readFileSync('./apps/HeIsRisen/main.js', 'utf8');

  // Instead of brittle brace extraction, we simply inject the whole script and mock its few global dependencies.
  // The test failed code review previously due to unmaintainable string parsing.
  await page.evaluate((code) => {
      // Mock global dependencies so the entire main.js parses successfully
      window.document.getElementById = () => null;
      window.AudioContext = class {};
      window.webkitAudioContext = class {};

      // Mock Phaser
      window.Phaser = {
          Utils: { Array: { Shuffle: (arr) => arr } },
          Math: { Between: () => 0 },
          GameObjects: {
              Container: class {},
              Sprite: class {},
              Rectangle: class {},
              Text: class {},
              Image: class {},
              Zone: class {}
          },
          Scene: class {},
          Game: class {}
      };

      // Create a mock local storage that doesn't trigger security blocks
      const mockStorage = {};
      Object.defineProperty(window, 'localStorage', {
          value: {
              getItem: (k) => mockStorage[k] || null,
              setItem: (k, v) => mockStorage[k] = String(v),
              removeItem: (k) => delete mockStorage[k],
              clear: () => { for (let key in mockStorage) delete mockStorage[key]; }
          },
          writable: true
      });

      // We run eval on the code so it is executed in the browser context.
      // Since it's just function/class definitions at the top level, it won't crash
      // as long as our basic Phaser mocks exist.
      try {
          eval(code);
      } catch (e) {
          console.error("Failed to parse main.js in test context: ", e);
      }

      // Ensure the functions we need are on window to be called below
      if (typeof initializeGameData === 'function') {
          window.testInitializeGameData = initializeGameData;
      }
  }, mainCode);

  async function runTest(name, corruptedState) {
      console.log(`\n--- Test: ${name} ---`);

      const result = await page.evaluate((stateStr) => {
          if (!window.testInitializeGameData) {
              return { crashed: true, error: "initializeGameData not found" };
          }

          // Setup mock registry and cache
          const mockRegistry = {
              data: {},
              set: function(key, val) { this.data[key] = val; },
              get: function(key) { return this.data[key]; },
              has: function(key) { return this.data.hasOwnProperty(key); }
          };

          const mockCache = {
              json: {
                  has: () => true,
                  get: (key) => {
                      if (key === 'symbols') return { symbols: [] };
                      if (key === 'map_sections') return [{ name: 'A', eggs: 1 }]; // Must match the fallback logic structure
                      return null;
                  }
              }
          };

          // Setup corrupted localStorage
          window.localStorage.setItem('heIsRisenGameState', stateStr);

          try {
              window.testInitializeGameData(mockRegistry, mockCache, false);
          } catch(e) {
              console.error("CRASH IN initializeGameData: ", e.message);
              return { crashed: true, error: e.message };
          }

          return mockRegistry.data;
      }, JSON.stringify(corruptedState));

      if (result.crashed) {
          console.log(`RESULT: FAILED - Application crashed (${result.error})`);
      } else {
          // If valid state loaded, length is 1. If fallback happened, length is TOTAL_EGGS (60).
          // If it accepted corrupt primitive array, it might be whatever was passed in.

          const eggData = result.eggData;
          if (!eggData || !Array.isArray(eggData)) {
              console.log(`RESULT: FAILED (No valid eggData array in registry)`);
          } else {
              const firstItem = eggData[0];
              const isCorruptIdNaN = firstItem && firstItem.eggId === 'NaN';
              const isCorruptPrimitive = typeof firstItem === 'number';

              if (isCorruptIdNaN || isCorruptPrimitive) {
                  console.log(`RESULT: FAILED (Accepted corrupt state)`);
              } else {
                  console.log(`RESULT: PASSED (Fell back safely or loaded valid state)`);
              }
              console.log(`Current eggData in Registry (first item):`, firstItem);
          }
      }
  }

  await runTest('Valid State', {
      eggData: [{ eggId: 1, section: 'A', x: 0, y: 0, collected: false }],
      sections: [{ name: 'A', eggs: [1] }],
      foundEggs: [],
      stampedSections: [],
      correctCategorizations: 0,
      currentScore: 0
  });

  await runTest('Corrupted Inner Array (NaN ID)', {
      eggData: [{ eggId: "NaN", section: 'A', x: 0, y: 0, collected: false }],
      sections: [{ name: 'A', eggs: [1] }],
      foundEggs: [],
      stampedSections: [],
      correctCategorizations: 0,
      currentScore: 0
  });

  await runTest('Corrupted Inner Array (Primitives)', {
      eggData: [1, 2, 3],
      sections: [{ name: 'A', eggs: [1] }],
      foundEggs: [],
      stampedSections: [],
      correctCategorizations: 0,
      currentScore: 0
  });

  await browser.close();
})();
