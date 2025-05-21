# Project Resource Optimizer

This repository contains the source code for a Project Resource Optimizer tool developed during my graduate studies.

## Overview

This tool aims to optimize task assignments in environments with multiple projects, tasks, and team members (resources). By setting objective functions and constraints, it optimizes project completion time and efficient resource utilization.

## Key Features

- Management of multiple projects and tasks
- Task assignment considering members' skills and available time
- Resource optimization to minimize objective functions (cost, time, etc.)
- Data import and export via Smartsheet integration
- Visualization of Pareto-optimal solutions

## Technologies Used

- Python
- DEAP (Distributed Evolutionary Algorithms in Python)
- NumPy
- Smartsheet API

## Setup

1. Clone the repository
   ```
   git clone https://github.com/yourusername/ProjectResourceOptimizer.git
   cd ProjectResourceOptimizer
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
   
   Main dependencies:
   - deap: Framework for genetic algorithms
   - numpy: Numerical computation library
   - smartsheet-python-sdk: Smartsheet API client
   - matplotlib: Graph visualization library
   - python-dotenv: Environment variable management library

3. Set up environment variables
   - Copy `.env.example` to `.env` and fill in the required information
   ```
   cp .env.example .env
   ```
   - Configure the Smartsheet API key and related sheet IDs in the `.env` file
   ```
   # Smartsheet API
   SMARTSHEET_API_KEY=your_api_key_here
   
   # Project IDs
   PROJECT1_PROJECTS_TASKS_SHEET_ID=your_project1_tasks_sheet_id
   PROJECT1_MEMBERS_SHEET_ID=your_project1_members_sheet_id
   # ...other project IDs...
   
   # Selected Project
   SELECTED_PROJECT=project4
   ```

## Usage

Configure the various settings in the `parameters.py` file and run with the following command:

```
python main.py
```

## License

This project is released under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Related Research

The master's thesis related to this research:
- [Research on Project Resource Optimization Using Evolutionary Algorithms](./thesis/masters_thesis_2023.pdf)

## Notes

- This code is published for educational and research purposes
- The Smartsheet API keys and sheet IDs included in the repository are samples and will not work in practice
