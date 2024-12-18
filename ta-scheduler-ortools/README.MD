# Local Installation

1. Navigate to the project folder.
2. Run the following command to install the package:
   
   ```bash
   pip install -e .

It is recommended to use a Python virtual environment manager like Conda or PyEnv for a more isolated setup. Create and activate a virtual environment before running the installation.

# User Guide
The scheduler algorithm, implemented using the Google OR-Tools constraint satisfaction library, can be executed with the following command:

   ```bash
   roster-tas

Make sure to navigate to the data directory before running the command:

   ```bash
   cd data


data/
│
├── availability/
│   ├── TA_availability_1.xlsx
│   ├── TA_availability_2.xlsx
│   └── ...
│   └── TA_availability_n.xlsx
│
├── availability_Template.xlsx
├── shift_list.csv
└── ta_list.csv


