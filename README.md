# Search and Display

An interactive search algorithm visualizer and benchmarking dashboard built with Pygame. Originally created for CS461 Intro to Artificial Intelligence (Professor Jesse Lowe), this tool lets you watch BFS, DFS, Iterative Deepening DFS, Greedy Best-First Search, and A* explore graphs in real time — then benchmark them head-to-head.

---

## Features

### Visualizer Mode
- **Five Search Algorithms**: BFS, DFS, Iterative Deepening DFS (IDDFS), Greedy Best-First Search, and A*
- **Three Graph Topologies**:
  - **Grid** — Classic NxN grid with configurable obstacle density
  - **Tree** — Randomly generated weighted graphs using the Barabási–Albert model, with edge costs displayed on each connection
  - **CSV** — Load real-world city data from `coordinates.csv` and `Adjacencies.txt` with distance-based edge weights
- **Playback Controls**: Play, Pause, and Step through the algorithm one node at a time
- **Speed Slider**: Adjust visualization speed from 0.1x to 5.0x
- **Heuristic Toggle**: Switch between Manhattan and Euclidean distance for Greedy/A*
- **Reproducible Seeds**: Type a seed number to regenerate the exact same graph
- **Live Timer**: Displays elapsed search time in real time on the control panel
- **Search Tree Panel**: A 5-tier depth visualization of the algorithm's exploration tree
- **Frontier Panel**: Live view of the open-list / priority queue contents
- **Completion Popup**: Reports Time Elapsed, Nodes Expanded, Path Length, Total Path Cost, and Peak Memory usage

### Benchmark Mode
- **Headless Batch Execution**: Run algorithms without visual rendering for accurate timing
- **Multi-Algorithm Selection**: Checkbox selection for any combination of the five algorithms
- **Complexity Presets**: Easy (20 nodes), Medium (100 nodes), Hard (500 nodes)
- **Configurable Runs**: Set the number of benchmark iterations (default: 5)
- **Performance Table**: Displays Mean/Std Time, Mean/Std Expanded nodes, and Peak Memory
- **Comparison Chart**: Auto-generated bar chart with error bars for visual comparison
- **Loading Overlay**: Animated spinner with transparent overlay during benchmark execution
- **Inverted Theme**: High-contrast blue dashboard theme for visual distinction

---

## Project Structure

```
Search Visualizer/
├── main.py              # Application controller: event loop, mode toggling, UI layout
├── environment.py       # Graph generation engine (Grid, Tree, CSV topologies via NetworkX)
├── renderer.py          # All Pygame drawing routines for both modes
├── ui_components.py     # Reusable UI widgets: Button, Slider, Checkbox, Dropdown, TextInput
├── constants.py         # Centralized window sizes, colors, and UI theme definitions
├── benchmark.py         # Headless batch runner and matplotlib chart generation
├── loading_overlay.py   # Animated loading spinner overlay for benchmark runs
├── bfs_agent.py         # Breadth-First Search agent
├── dfs_agent.py         # Depth-First Search agent
├── iddfs_agent.py       # Iterative Deepening DFS agent
├── greedy_agent.py      # Greedy Best-First Search agent
├── astar_agent.py       # A* Search agent (uses actual edge weights)
├── binary_tree.py       # VisualizationTree data structure for the search tree panel
├── search.py            # Original standalone BFS/DFS implementations (legacy, from Part A)
├── coordinates.csv      # City coordinate data for CSV topology mode
├── Adjacencies.txt      # City adjacency definitions for CSV topology mode
└── requirements.txt     # Python dependencies
```

---

## Installation and Running

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation
1. Clone or extract the project files to a directory of your choice
2. Open a terminal/command prompt and navigate to the project directory
3. Create a virtual environment (recommended):
   ```
   python -m venv .venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   Additional packages needed (install if not already present):
   ```
   pip install networkx matplotlib numpy
   ```

### Running the Application
1. Ensure your virtual environment is activated
2. Run the main application:
   ```
   python main.py
   ```

---

## How to Use

### Visualizer Mode (Default)

The application opens in Visualizer Mode with three panels:
- **Left Panel**: The graph canvas where pathfinding is visualized
- **Middle Panel**: Real-time search tree visualization (5-tier depth view)
- **Right Panel**: Controls for configuration and algorithm selection

#### Step-by-Step
1. **Choose a Topology**: Click `Topology: Grid` to cycle between Grid, Tree, and CSV.
2. **Configure the Graph**:
   - **Grid**: Adjust the `Obstacles` slider to change wall density.
   - **Tree**: Adjust `N Nodes` (5–50) and `Branches` (1–5) sliders. Type a seed number to reproduce a specific graph. Number edge weights (1–10) are displayed on each connection.
   - **CSV**: Loads `coordinates.csv` and `Adjacencies.txt` from the project directory automatically. Use `Rand Start` / `Rand Goal` to pick new endpoints.
3. **Click `Randomize Graph`** to generate a new random graph (updates the seed automatically).
4. **Select an Algorithm**: Click `BFS`, `DFS`, `IDDFS`, `Greedy`, or `A*`.
5. **Toggle Heuristic** (Greedy/A* only): Click `Heuristic: Manhat` to switch between Manhattan and Euclidean distance.
6. **Control Playback**:
   - `Play` — Start continuous execution
   - `Pause` — Pause execution
   - `Step` — Advance one step at a time
   - `Speed` slider — Adjust from 0.1x to 5.0x
7. **View Results**: When the search completes, a popup displays:
   - Time Elapsed
   - Nodes Expanded
   - Path Length
   - Path Cost (sum of edge weights along the found path)
   - Peak Memory (maximum nodes stored in frontier + visited)
8. **Click `Reset`** to clear the current search and try another algorithm on the same graph.

### Benchmark Mode

1. **Click `Mode: Visualizer`** at the top to switch to `Mode: Benchmark`.
2. **Select Algorithms**: Check any combination of BFS, DFS, ID-DFS, Greedy, and A*.
3. **Choose Complexity**: Select Easy, Medium, or Hard from the dropdown.
4. **Set Runs**: Type the number of benchmark iterations in the Runs input (default: 5).
5. **Click `Run Benchmark`**: A loading spinner appears while algorithms execute headlessly.
6. **Review Results**: The performance table and comparison chart appear side-by-side:
   - **Table**: Mean/Std Time, Mean/Std Expanded, Peak Memory for each algorithm
   - **Chart**: Bar chart with standard deviation error bars

---

## Understanding the Results

| Metric | Meaning |
|--------|---------|
| **Time Elapsed** | Wall-clock time from first step to goal found |
| **Nodes Expanded** | Total unique nodes the algorithm visited |
| **Path Length** | Number of nodes in the solution path |
| **Path Cost** | Sum of edge weights along the solution path (relevant for weighted graphs) |
| **Peak Memory** | Maximum number of nodes stored simultaneously in frontier + visited sets |
| **Std (Standard Deviation)** | How much performance varied across runs — lower is more consistent |
| **Error Bars (Chart)** | Visual representation of standard deviation — shorter bars = more reliable |

### Key Algorithmic Differences on Weighted Graphs
- **A*** finds the **optimal (lowest-cost) path** on weighted graphs by combining actual path cost with a heuristic estimate.
- **BFS** finds the **shortest path by hop count** but ignores edge weights entirely.
- **DFS** and **IDDFS** find **a** path but make no optimality guarantees.
- **Greedy** chases the heuristic greedily — fast but not guaranteed optimal.

---

## Development Notes

This project was created with developmental assistance from Gemini 3.1 Pro for conceptual study and Github Copilot (ChatGPT 4o / Claude Sonnet 4) for coding. Comments will illustrate what is personally written, and what is generated.