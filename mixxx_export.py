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

angles_all = np.concatenate([angles] * 3)
radii_all = np.concatenate([df["bpm"] / 2, df["bpm"], df["bpm"] * 2])

# 3. Filter to only values >80 and <=240 BPM
mask = (radii_all > 80) & (radii_all <= 240)
angles_filt = angles_all[mask]
radii_filt = radii_all[mask]

# 4. Create the polar scatter plot
fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
ax.scatter(angles_filt, radii_filt)

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
