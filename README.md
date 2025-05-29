# Project Title: StarCraft II AI Bots

**Project Overview:**
This project is a collection of AI bots for StarCraft II, developed using Python and the python-sc2 library. It includes bots with different strategies and a tool for analyzing game replays. The primary goal is to explore various AI techniques in the context of StarCraft II.

**Features:**
*   Multiple Starcraft II bot implementations.
*   `han`: A Terran bot potentially using machine learning techniques (details in `han/README.md`).
*   `lishimin`: Protoss bots employing strategies like cannon rushes (`LiShiMinBot`) and multi-pylon builds (`MultiPylonBot`).
*   Replay analysis tool (`analysis/sc2reader_analyzer.py`) to extract build orders, unit production, upgrades, and generate performance graphs.
*   Scripts to run bots locally against the computer or other bots.

**Directory Structure:**
*   `README.md`: This file, providing an overview of the project.
*   `LICENSE`: Contains the project's license information.
*   `han/`: Contains the "han" Terran bot, including its specific README.
    *   `han/han.py`: Main logic for the HanBot.
    *   `han/run.py`: Script to run the HanBot.
*   `lishimin/`: Contains the "lishimin" Protoss bots.
    *   `lishimin/lishimin.py`: Main logic for the LiShiMinBot (cannon rush).
    *   `lishimin/multi_pylon.py`: Logic for the MultiPylonBot.
    *   `lishimin/run.py`: Script to run the lishimin bots.
*   `analysis/`: Contains tools for game replay analysis.
    *   `analysis/sc2reader_analyzer.py`: Script to parse replays and extract game data.
*   `run_local_games.py`: A script to easily run games between different bots or against the computer.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.

**Getting Started:**

**Prerequisites:**
*   Python 3.7+
*   StarCraft II Game Client (ensure it's installed and updated)
*   The `python-sc2` library: `pip install sc2`
*   For replay analysis (`analysis/sc2reader_analyzer.py`):
    *   `sc2reader`: `pip install sc2reader`
    *   `matplotlib`: `pip install matplotlib`
    *   `numpy`: `pip install numpy`

**Map Installation:**
1.  Download the latest map pack from [AI Arena Maps](https://aiarena.net/wiki/maps/)
2.  Extract the downloaded map files
3.  Place the maps in your StarCraft II maps directory:
    *   Windows default location: `C:\Program Files (x86)\StarCraft II\Maps\`
    *   macOS default location: `/Applications/StarCraft II/Maps/`
    *   If the `maps` folder doesn't exist, create it
    *   Note for Linux users: the folder name is case sensitive

**Installation:**
1.  Clone this repository:
    ```bash
    git clone <repository_url>
    cd sc2_bots
    ```
2.  Install the required Python libraries. It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

    # Install core library for bot development
    pip install python-sc2

    # For replay analysis using analysis/sc2reader_analyzer.py, also install:
    pip install sc2reader matplotlib numpy
    ```

**Running the Bots:**

*   **Using individual bot runners:**
    Each bot directory (`han/`, `lishimin/`) contains a `run.py` script that can be configured to run that specific bot.
    ```bash
    cd han
    python run.py
    ```
    ```bash
    cd lishimin
    python run.py
    ```
    You might need to edit these `run.py` files to specify opponents, maps, etc.

*   **Using `run_local_games.py`:**
    This script (if it exists and is configured) can be used to run games between different bots or against the built-in AI.
    ```bash
    python run_local_games.py
    ```
    *(Note: Based on the `ls()` output, this file exists. Its functionality is assumed for this README.)*

**Available Bots:**

*   **HanBot (`han/`)**
    *   Race: Terran
    *   Strategy: This bot is described as an ML-based bot. For more details on its specific strategies and development, please refer to its dedicated README: `han/README.md`.
*   **LiShiMin Bots (`lishimin/`)**
    *   Race: Protoss
    *   `LiShiMinBot`: Implements a cannon rush strategy.
    *   `MultiPylonBot`: Focuses on a strategy involving multiple pylons (details can be inferred from `lishimin/multi_pylon.py`).

**Replay Analysis (`analysis/sc2reader_analyzer.py`):**
This project includes a script to analyze StarCraft II replay files (`.SC2Replay`).

**Features:**
*   Extracts build orders for each player.
*   Summarizes unit production counts.
*   Lists completed upgrades with timestamps.
*   Generates graphs for resource collection rates (minerals, vespene) over time.
*   Generates graphs for unit counts over time for each player.

**Usage:**
1.  Ensure you have `sc2reader`, `matplotlib`, and `numpy` installed.
2.  Run the script from the command line, providing the path to a replay file:
    ```bash
    python analysis/sc2reader_analyzer.py /path/to/your/replay.SC2Replay
    ```
    Or, if you are in the root directory of the project:
    ```bash
    python analysis/sc2reader_analyzer.py path/to/your/replay.SC2Replay
    ```
3.  The script will print analysis to the console and save output files (build orders, unit lists, graphs) in the same directory as the replay file, with extensions like `.build_order.txt`, `.units.txt`, `.resources.png`, `.units.png`.

**Example:**
```bash
python analysis/sc2reader_analyzer.py han/han.SC2Replay 
```
*(Assuming a replay file named `han.SC2Replay` might exist in the `han/` directory as per `han/run.py`)*

**Contributing:**
Contributions to this project are welcome! Here are some ways you can contribute:
*   Developing new bots with different strategies.
*   Improving existing bots.
*   Enhancing the replay analysis tool.
*   Reporting bugs or suggesting new features.

Please follow these general guidelines:
1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes, including clear comments and tests if applicable.
4.  Ensure your code adheres to any existing style guidelines (e.g., run a linter).
5.  Submit a pull request for review.

**License:**
This project is licensed under the terms of the LICENSE file. Please see the `LICENSE` file in the root directory for more details. (Currently, it appears to be an MIT License based on typical open-source projects, but confirm this by checking the LICENSE file content if possible. If `LICENSE` file content is not available, use this general statement).
