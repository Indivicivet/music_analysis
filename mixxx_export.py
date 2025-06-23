import os
from pathlib import Path
import sqlite3

import pandas as pd
import numpy as np
import plotly.express as px

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
angle_map = {key_id: idx for idx, key_id in enumerate(circle_order)}

df["key_pos"] = df["equiv_major_key"].map(angle_map)

df_all = pd.concat(
    [
        df.assign(bpm=df["bpm"] * bpm_scale, key_pos_ext=df["key_pos"] + shift)
        for bpm_scale in [1 / 2, 1, 2]
        for shift in [-12, 0, 12]
    ],
    ignore_index=True,
)
MIN_KEY = -3
MAX_KEY = 14
df_filt = df_all[
    (df_all["key_pos_ext"] >= MIN_KEY)
    & (df_all["key_pos_ext"] <= MAX_KEY)
    & (df_all["bpm"] > 80)
    & (df_all["bpm"] <= 240)
]

fig = px.scatter(
    df_filt,
    x="key_pos_ext",
    y="bpm",
    color=df_filt["key_is_minor"].map({False: "Major", True: "Minor"}),
    hover_data=["artist", "title", "key", "bpm"],
    labels={"key_pos_ext": "Circle‑of‑Fifths Position", "bpm": "BPM", "color": "Mode"},
)

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
fig.update_layout(
    xaxis={
        "tickmode": "array",
        "tickvals": list(range(MIN_KEY, MAX_KEY + 1)),
        "ticktext": [
            key_labels[circle_order[pos % 12]] for pos in range(MIN_KEY, MAX_KEY + 1)
        ],
    },
    legend={"title": "Mode"},
    title="BPM vs Circle‑of‑Fifths (interactive)",
)
fig.show()
