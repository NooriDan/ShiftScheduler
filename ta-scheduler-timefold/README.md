# TA Scheduler (Python)

This directory contains the scheduler logic used in our ClassBridge platform. We have made this opensource to encourage further collaboration. 
A command-line tool to generate optimized TA schedules by assigning lessons/labs/tut (shifts) to TAs, using Timefold. Try the new TABRIZ edition! check out the [source code](/src/hello_world), if interested.

---

## Features

- **Flexible data sources**: built-in demo data or your own CSVs  
- **Multiple solving methods**: blocking solver, solver-manager, or progress-bar mode  
- **Constraint versions**: switch between predefined constraint sets (e.g. `default`, `tabriz`)  
- **Benchmark mode**: run multiple seeds, modify behaviour by changing the `benchmark_config.json` file, gather score analyses, and dump JSON/PKL results  
- **Post-solve analysis**: view broken constraints, match counts, and scoring breakdown  

---

## Prerequisites

- **Python 3.10+**  
  Download & install from [python.org](https://www.python.org/downloads/)  
- **Java 17+** (required by Timefold/OptaPlanner)  
  Install via [Sdkman](https://sdkman.io): 
  ``sdk install java``

- **git** (for cloning)

---

## Installation

1. **Clone the repo**  
   `
   git clone https://github.com/TimefoldAI/timefold-quickstarts.git
   cd timefold-quickstarts/python/hello-world
   `

2. **Create & activate a virtual environment**  
   ```shell
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the package**  
   ```shell
   pip install -e .
   ```

---

## Quick Start

- **Show help**  
  ```shell
  timefold-run-demo --help
  ```

- **Run default demo** (weekly random data)  
  ```shell
  timefold-run-demo
  ```

- **Use custom CSVs & availability**  
  ```shell
  timefold-run-demo \
    --overwrite \
    --ta_csv_path path/to/ta_list.csv \
    --shift_csv_path path/to/shift_list.csv \
    --availability_folder path/to/availability/
  ```

- **Run benchmark** (e.g. 10 runs, JSON+PKL output)  
  ```shell
  timefold-run-benchmark \
    --demo_data_select benchmark-semester \
    --constraint_version tabriz
  ```

---

## Command-Line Reference

All flags apply to both `timefold-run-demo` and `timefold-run-benchmark` (as relevant):
[options="header"]
|===
| Flag                      | Type   | Default                                      | Description
| +--ta_csv_path+           | str    | +ta_list.csv+                                | Path to your TA list CSV.
| +--shift_csv_path+        | str    | +shift_list.csv+                             | Path to your Shift list CSV.
| +--availability_folder+   | str    | +availability/+                              | Folder of per-TA availability CSVs.
| +--overwrite+             | bool   | +false+                                      | Load CSV/folder data instead of demo data.
| +--constraint_version+    | str    | +default+                                    | Constraint set to apply (default, tabriz, …).
| +--demo_data_select+      | str    | +demo_data_weekly_scheduling-random (demo)+  | Which built-in demo dataset to load.
| +--solving_method+        | str    | +solver_manager+                             | Solver instantiation: solver_manager, blocking, or tqdm.
| +--use_config_xml+        | bool   | +false+                                      | Load solver settings from solver_config.xml.
| +--path_to_config_xml+    | str    | +None+                                       | Custom path to your solver_config.xml.
|===


**Benchmark-only flags**:
[options="header"]
|===
| Flag                   | Type   | Default             | Description
| +--demo_data_select+   | str    | +benchmark-weekly+  | Choose +benchmark-weekly+ or +benchmark-semester+.
| +--constraint_version+ | str    | +default+           | Constraint set for benchmark.
|===

---

## Demo Data vs. Custom Data

### Demo Data

- Stored in Python, randomized each run (seeded).  
- Variants:  
  - `demo_data_weekly_scheduling-random`  
  - `benchmark-semester`  
  - …  

### Custom Data

Provide three inputs:

1. **`ta_list.csv`**  
   ```csv
   ta_id,name,skill_level,...
   ```

2. **`shift_list.csv`**  
   ```csv
   shift_id,week_id,day_id,room_id,start_time,end_time,required_skill,...
   ```

3. **`availability/`**  
   Folder with one `<ta_id>.csv` per TA, each containing:  
   ```csv
   shift_id,available (0/1),desired (0/1),undesired (0/1)
   ```

---

## Benchmark Mode

Run multiple seeds to evaluate solver performance:

```shell
timefold-run-benchmark \
  --demo_data_select benchmark-weekly \
  --constraint_version default \
  --use_config_xml \
  --path_to_config_xml path/to/solver_config.xml
```

**Output directory**:  
```
results/<constraint_version>/<YYYY-MM-DD_HH-MM-SS>/
├── benchmark_results.json   # Detailed scores & metadata
└── solutions.pkl (or baseline.pkl)
```

---

## Logging & Analysis

- Default log level: `INFO`.  
- View broken constraints via `ScoreAnalysis` in `BenchmarkRunnerBase.process_score_analysis()`.  
- Future: enable `solver.post_process_solution(..., log_analysis=True)` for per-constraint details.

---

## Extending Constraints

1. Open `hello_world/constraints.py`.  
2. Add a new entry to `constraints_provider_dict`, e.g.:

   ```python
   constraints_provider_dict['myversion'] = my_constraints_function
   ```

3. Run with:

   ```shell
   timefold-run-demo --constraint_version myversion
   ```

---

## Contributing

1. Fork the repo and create a feature branch.  
2. Write clear commit messages and add/update tests.  
3. Open a PR against `main`, referencing relevant issues.  
4. Ensure CI (GitHub Actions) passes.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
```
