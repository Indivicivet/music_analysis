import os
from pathlib import Path
import sqlite3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
conn.close()

df["key_is_minor"] = df["key_id"] > 12
df["equiv_major_key"] = df["key_id"]
df.loc[df["key_is_minor"], "equiv_major_key"] = (df["key_id"] - 13 + 3) % 12 + 1
print(df.head().to_string())

circle_order = [1, 8, 3, 10, 5, 12, 7, 2, 9, 4, 11, 6]
angle_map = {key_id: (2 * np.pi * idx / 12) for idx, key_id in enumerate(circle_order)}

angles = df["equiv_major_key"].map(angle_map)

r_original = df["bpm"]
r_double = df["bpm"] * 2

fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
ax.scatter(angles, r_original)
ax.scatter(angles, r_double)

key_labels = {
    1: "C",
    8: "G",
    3: "D",
    10: "A",
    5: "E",
    12: "B",
    7: "Gb",
    2: "Db",
    9: "Ab",
    4: "Eb",
    11: "Bb",
    6: "F",
}
tick_angles = [angle_map[k] for k in circle_order]
tick_labels = [key_labels[k] for k in circle_order]
ax.set_xticks(tick_angles)
ax.set_xticklabels(tick_labels)

ax.set_rlabel_position(90)
ax.set_ylabel("BPM", labelpad=20)
plt.show()
