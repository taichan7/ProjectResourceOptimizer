# Project Resource Optimizer

This repository contains the source code for a Project Resource Optimizer tool developed during my graduate studies.

## Overview

This research prototype explores task assignments across multiple projects and team
members using evolutionary multi-objective optimization. The implemented objectives
are total assignment cost and the standard deviation of members' allocated labor
days. Penalties cover overlapping assignments, budget overruns and missing skills.
It does not guarantee a globally optimal or constraint-feasible staffing plan.

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
   git clone https://github.com/taichan7/ProjectResourceOptimizer.git
   cd ProjectResourceOptimizer
   ```

2. Create an isolated environment and install dependencies. For live API use,
   use a current Python installation with supported OpenSSL rather than an old
   macOS system Python/LibreSSL build.
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```
   
   Main dependencies:
   - deap: Framework for genetic algorithms
   - numpy: Numerical computation library
   - smartsheet-python-sdk: Smartsheet API client
   - matplotlib: Graph visualization library
   - python-dotenv: Environment variable management library
   - imageio: PNG/GIF output

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
   Only the repository's own `.env` is loaded; existing environment variables take
   precedence. The selected project's input sheet IDs must be positive numeric IDs.
   Export template/folder IDs are required only when enabling Smartsheet writes.
   Use disposable test sheets and anonymized project/member data. Never commit or
   share `.env`, API keys, real participant data or generated results.

## Usage

Review the experiment grid in `parameters.py` before running; the default grid
can be computationally expensive. By default, Smartsheet access is **read-only**:
input data is fetched from the API, and CSV/PNG/GIF results are written to the
git-ignored `results/<timestamp>/` directory in this repository.

```
python main.py
```

To deliberately enable remote exports to a confirmed disposable template/folder:

```bash
python main.py --allow-smartsheet-writes
```

This opt-in copies the configured template and replaces rows in the new output
sheet for each experiment. Replacement validates columns and rows and adds new
rows before deleting old ones. It is **not a transaction**: cleanup failure can
leave both old and new rows. Inspect failed exports instead of blindly retrying.
Programmatic `SmartsheetHandler` callers must also explicitly pass
`allow_writes=True`. CSV text that could be interpreted as a spreadsheet formula
is prefixed with an apostrophe; numerical objective values are unchanged.

## Validation

Run the offline tests without a Smartsheet account or real credentials:

```bash
MPLBACKEND=Agg python -m unittest discover -s tests -v
python main.py --help
```

The tests mock every Smartsheet request and check write opt-in, preservation of
existing rows on failed exports, configuration, CSV text safety and plot outputs.
They do not establish live API compatibility, production suitability or exact
reproduction of the thesis experiments.

## License

This project is released under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Related Research

The master's thesis related to this research:
- [Research on Project Resource Optimization Using Evolutionary Algorithms](./thesis/masters_thesis_2023.pdf)
- [Thesis abstract](./thesis/thesis_abstract_2023.pdf)

## Notes

- This code is published for educational and research purposes
- `.env.example` contains placeholders, not working credentials or sheet IDs
- Evolutionary runs are stochastic; library versions, data and random seeds affect
  results. Review feasibility and constraints before using an assignment.
- Console output and generated files may contain project/member information from
  your input sheets. Use synthetic or anonymized data when sharing outputs.
- The thesis research content and optimization objective/constraint formulas are
  preserved. The public abstract omits the student-number field for privacy.
