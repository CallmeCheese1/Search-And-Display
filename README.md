# Search and Display

This is the repository for the first programming assignment for Intro to Artificial Intelligence, taught by Professor Jesse Lowe. It will be an interactive tool that generates an NxN grid, places an agent and a goal, and visualizes either a BFS or DFS algorithm.

## Project Structure

Environment.py -- Defines the grid itself, nodes, and how we can get the neighbors of a particular node.   
Search.py -- Provides the segmented functionality and logic for both BFS and DFS.   
main.py -- Contains the pygame logic for visualizing the grid, creating the agent, and displaying their path.

## Installation and Running

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation
1. Extract the project files to a directory of your choice
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

### Running the Application
1. Ensure your virtual environment is activated
2. Run the main application:
   ```
   python main.py
   ```
3. The visualizer window will open with three panels:
   - **Left Panel**: The grid where pathfinding is visualized
   - **Middle Panel**: Tree visualization showing the search process
   - **Right Panel**: Controls for selecting algorithms and adjusting speed

### How to Use
1. Click "Create BFS Agent" or "Create DFS Agent" to start a search algorithm
2. Use the speed slider to adjust visualization speed (0.1x to 5.0x)
3. Click "Reset" to generate a new grid and start over
4. Watch as the algorithm explores the grid and finds a path from the green start node to the red goal node

## Development Notes

This project was created with developmental assistance from Gemini 3.1 Pro for conceptual study and Github Copilot (ChatGPT 4o / Claude Sonnet 4) for coding. Comments will illustrate what is personally written, and what is generated.