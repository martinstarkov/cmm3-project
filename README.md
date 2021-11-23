### Minimum required Python version: 3.7.

# How to run
1. Open a terminal in the same directory as this file.
2. Run the command: `python -m pip install -r requirements.txt` to install all required modules.
3. Run the command: `python interface.py` to open the user interface.
4. Note that some machines may require replacing `python` with `python3` or `py`

If having issues with tkinter, check that it was installed alongside the default Python installation from https://www.python.org/

### File descriptions
- `group_8_report.pdf` contains the report accompanying the application.
- `interface.py` implements all user interface related functionality and acts as an entry point to the application.
- `simulation.py` implements the mathematics and physics relating to the fluid simulation.
- `utility.py` contains fairly general utility functions used throughout all files.
- `validation.py` implements a class which handles error validation related tasks.
- `config.json` stores information relating to user interface generation, such as input field default values.
- `requirements.txt` contains python module dependencies for this project.
- `velocityCMM3.dat` sample velocity field provided by the university.
- `reference_solution_1D.dat` reference data for a 64x1 concentration grid.
- `.gitignore` specifies which file types should be ignored by GitHub.

Enjoy!
