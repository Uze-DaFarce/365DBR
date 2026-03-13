# He Is Risen - Easter Egg Hunt Game

## Overview
"He Is Risen" is a web-based game designed to help children explore the meaning of Easter. Players hunt for Easter eggs hidden across a map of Yellowstone National Park. Each egg contains a symbol that represents either a Christian concept (related to the Resurrection and the Gospel) or a Worldly/Pagan concept.

After collecting eggs, players enter the "EggZam Room" where they sort the symbols they've found, learning why each is considered Christian or Worldly through scripture and explanations.

## Game Goals
- **Total Eggs**: 60
- **Distribution**:
    - 30 Unique Christian Symbols
    - 30 Unique Worldly/Pagan Symbols
- **Objective**: Find all eggs and correctly categorize them to learn the true meaning of Easter.

## Current Status
**⚠️ Work In Progress ⚠️**

This project is currently being revived and documented. It was previously left unfinished.

### Known Issues
- **Platform Discrepancies**: There are separate versions for Desktop (root) and Mobile (`m/`), which have diverged in logic.

- **Bugs**:
    - Mobile version scaling and "magnifying glass" mechanic need tuning.

## Development
The game uses the [Phaser 3](https://phaser.io/) framework.

### Running Locally
To run the game locally, you need a local web server (Phaser requires this to load assets due to CORS/security policies).

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the server:
   ```bash
   npm start
   ```
3. Open your browser to `http://127.0.0.1:8080`.

### Directory Structure
- `/`: Desktop version source code.
- `/m/`: Mobile version source code.
- `/assets/`: Shared images and data.

## License
MIT
