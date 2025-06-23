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

df["key_is_minor"] = df["key_id"] > 12
df["equiv_major_key"] = df["key_id"]
df.loc[df["key_is_minor"], "equiv_major_key"] = (df["key_id"] - 13 + 3) % 12 + 1
print(df.head().to_string())

conn.close()
