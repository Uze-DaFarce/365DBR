# Mt. Sinai LLC - Monorepo

**Faith-Centered Business Services & Ethical AI**

This monorepo contains the collected source code for all of Mt. Sinai LLC's web-based ministry projects. We are dedicated to providing professional business services that honor God, specializing in ethical AI implementation, bookkeeping, web design, and application solutions.

## Mission

"Each task, even the most ordinary, is sacred when done for God. We are called to work with excellence, integrity, and devotion, knowing that Christ Himself is whom we serve as we serve our clients."

## Applications

This repository is organized into the following applications:

*   **/apps/365dbr**: A "Read the Bible in a Year" plan that takes less than 15 minutes a day.
*   **/apps/heisrisen**: An interactive Christian Easter Egg Hunt game.
*   **/apps/mtsinai**: The main corporate website for Mt. Sinai LLC.

## 365DBR: Technical Overview

The `365DBR` application includes Python scripts to generate and manage a balanced 365-day Bible reading plan.

### Key Files (`apps/365dbr`)

*   **`generate_readings.py`**: Calculates the daily reading schedule.
*   **`fetch_readings.py`**: Downloads scripture data from `api.bible`.
*   **`compile_site.py`**: Generates the static HTML for the application.
*   **`data/readings.json`**: The master schedule for the reading plan.

### Setup Instructions

1.  **Prerequisites**: Python 3.x installed.
2.  **API Key**: You need a free API Key from [api.bible](https://scripture.api.bible/).
3.  **Environment Variable**: Set your API key in your terminal.
    *   **PowerShell:** `$env:API_BIBLE_KEY = "your_32_char_api_key"`
    *   **Bash/Linux:** `export API_BIBLE_KEY="your_32_char_api_key"`
4.  **Install Dependencies**:
    ```bash
    pip install -r apps/365dbr/requirements.txt
    playwright install
    ```

### Usage

All commands should be run from the root of the monorepo.

1.  **Generate Plan** (Optional):
    ```bash
    python apps/365dbr/generate_readings.py
    ```
2.  **Fetch Readings**:
    ```bash
    # Fetch a single day
    python apps/365dbr/fetch_readings.py --day 0201

    # Fetch a full month
    python apps/365dbr/fetch_readings.py --month 02

    # Fetch the entire year
    python apps/365dbr/fetch_readings.py --all
    ```
3.  **Compile Site**:
    ```bash
    python apps/365dbr/compile_site.py
    ```

## Contact

*   **Email**: [truth@mt-sin.ai](mailto:truth@mt-sin.ai)
*   **Phone**: (206) 718-9780
*   **Location**: Conrad, MT
