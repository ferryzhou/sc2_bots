# Project Title: StarCraft II AI Bots

**Project Overview:**
This project is a collection of AI bots for StarCraft II, developed using Python and the python-sc2 library. It includes bots with different strategies and a tool for analyzing game replays. The primary goal is to explore various AI techniques in the context of StarCraft II.

**Features:**
*   Multiple Starcraft II bot implementations.
*   `han`: HanBot V2.0, a rule-based Terran bio/mech macro bot with scouting, cheese detection, and army micro. It can beat the built-in cheater AIs (details in `han/README.md`).
*   `lishimin`: Protoss bots employing strategies like cannon rushes (`LiShiMinBot`) and multi-pylon builds (`MultiPylonBot`).
*   `phoenix`: PhoenixBot, a Protoss bot built on the ares-sc2 framework with data-driven openings (details in `phoenix/README.md`).
*   `griffin`: GriffinBot, a Terran bio+tank bot built on ares-sc2, the Terran counterpart of PhoenixBot (details in `griffin/README.md`).
*   Replay analysis tool (`analysis/sc2reader_analyzer.py`) to extract build orders, unit production, upgrades, and generate performance graphs.
*   `bot_profiles/`: A scouting dossier on the AI Arena ladder opponents GriffinBot faces — per-bot build order, economy trajectory, strengths/weaknesses, and the counter, derived from replay data. See `OPPONENTS.md` for the framework on playing a field of deterministic bots.
*   Scripts to run bots locally against the computer or other bots.

**Directory Structure:**
*   `README.md`: This file, providing an overview of the project.
*   `LICENSE`: Contains the project's license information.
*   `han/`: Contains the "han" Terran bot, including its specific README.
    *   `han/han.py`: Main logic for the HanBot, plus a `main()` entry point to run it against the built-in AI.
    *   `han/run.py`: Script to run the HanBot locally or on a ladder server.
*   `lishimin/`: Contains the "lishimin" Protoss bots.
    *   `lishimin/lishimin.py`: Main logic for the LiShiMinBot (cannon rush).
    *   `lishimin/multi_pylon.py`: Logic for the MultiPylonBot.
    *   `lishimin/run.py`: Script to run the lishimin bots.
*   `phoenix/`: Contains the "phoenix" Protoss bot (ares-sc2), including its specific README.
*   `griffin/`: Contains the "griffin" Terran bot (ares-sc2), including its specific README.
    *   `griffin/bot/main.py`: Main logic for the GriffinBot.
    *   `griffin/terran_builds.yml`: Data-driven opening build orders.
    *   `griffin/run.py`: Script to run the GriffinBot locally or on a ladder server.
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

    HanBot can also be run directly against a built-in cheater AI (currently a CheatInsane Zerg; edit `main()` in `han/han.py` to change the opponent race and difficulty):
    ```bash
    python han/han.py
    ```

*   **Using `run_local_games.py`:**
    This script runs a game between HanBot (Terran) and LiShiMinBot (Protoss) and saves the replay to `replays/han_vs_lishimin.SC2Replay`.
    ```bash
    python run_local_games.py
    ```

**Available Bots:**

*   **HanBot (`han/`)**
    *   Race: Terran
    *   Strategy: A rule-based bio/mech macro bot (V2.0). It plays a marine/marauder/siege tank composition supported by medivacs and ravens, manages its economy (SCV production, MULE calldowns, orbital upgrades, base expansions), builds addons, and researches infantry upgrades through engineering bays and an armory.
    *   Notable behaviors from recent development:
        *   Early game worker scouting plus ongoing medivac/raven scouting of the map.
        *   Cheese detection in the first 3 minutes, with a dedicated early game defense mode.
        *   Base attack detection with counter-attack logic when defending with a superior force.
        *   Siege tank micro (siege/unsiege based on enemy distance and nearby enemy targeting).
        *   Strategic building placement that avoids blocking expansion locations.
    *   It can consistently beat the built-in cheater AIs (e.g., Protoss CheatMoney and Terran CheatVision).
    *   For development history, see its dedicated README: `han/README.md`.
*   **LiShiMin Bots (`lishimin/`)**
    *   Race: Protoss
    *   `LiShiMinBot`: Implements a cannon rush strategy.
    *   `MultiPylonBot`: Focuses on a strategy involving multiple pylons (details can be inferred from `lishimin/multi_pylon.py`).
*   **PhoenixBot (`phoenix/`)**
    *   Race: Protoss
    *   Strategy: Built on the ares-sc2 framework. Data-driven openings (`phoenix/protoss_builds.yml`) executed by the ares build runner, then ares macro controllers and stalker-based micro. See `phoenix/README.md`.
*   **GriffinBot (`griffin/`)**
    *   Race: Terran
    *   Strategy: The Terran counterpart of PhoenixBot, sharing its ares-sc2 architecture. Data-driven openings (`griffin/terran_builds.yml`), then marine/marauder/siege tank/medivac with stim and siege micro, orbital/MULE management, and supply depot raise/lower. See `griffin/README.md`.

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
This project is licensed under the MIT License. See the `LICENSE` file in the root directory for details.
