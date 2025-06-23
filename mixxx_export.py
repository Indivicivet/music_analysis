import os
from pathlib import Path
import sqlite3

import pandas as pd

conn = sqlite3.connect(
    database=(
        "file:"
        + str(Path(os.getenv("LOCALAPPDATA")) / "Mixxx" / "mixxxdb.sqlite")
        + "?mode=ro"
    ),
    uri=True,
)

cur = conn.cursor()
df = pd.read_sql_query(
    """SELECT
    artist,
    title,
    bpm,
    key,
    key_id
FROM library;
""",
    conn,
)
print(df.head())

conn.close()

