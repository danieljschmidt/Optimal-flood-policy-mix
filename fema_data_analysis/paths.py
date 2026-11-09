# Location of the FEMA data folder: fema.db, the OpenFEMA v3 parquet files and the
# FHFA land-price file.  Shared by all scripts in fema_data_analysis/.
#
# Set the environment variable FEMA_DATA_DIR to use another folder; otherwise the
# first existing folder in DATA_DIRS is used.  Add your own folder to the list.

import os
from pathlib import Path

DATA_DIRS = [
    Path(r"C:\Users\TPRINS\OneDrive - UvA\Documenten\Python files insurance-aid\Code August 2026\fema_data_analysis\data"),
    Path(r"C:\Users\dschm\Documents\Data\FEMA"),
]
if os.environ.get("FEMA_DATA_DIR"):
    DATA_DIR = Path(os.environ["FEMA_DATA_DIR"])
    if not DATA_DIR.exists():   # an explicit override must not silently fall back
        raise FileNotFoundError(f"FEMA_DATA_DIR={DATA_DIR} does not exist")
else:
    DATA_DIR = next((d for d in DATA_DIRS if d.exists()), None)
if DATA_DIR is None:
    raise FileNotFoundError(
        "No FEMA data folder found. Set FEMA_DATA_DIR or add your folder to DATA_DIRS "
        f"in {Path(__file__).resolve()}. Tried: {[str(d) for d in DATA_DIRS]}"
    )
