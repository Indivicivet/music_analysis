import os
from pathlib import Path
import sqlite3

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.offline as pyo
import webbrowser

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
    library.artist,
    library.title,
    library.bpm,
    library.key,
    library.key_id,
    track_locations.location
FROM library
LEFT JOIN track_locations ON library.location = track_locations.id
""",
    conn,
)
conn.close()

df["file_path"] = df["location"].fillna("").astype(str)

df["key_is_minor"] = df["key_id"] > 12
df["equiv_major_key"] = df["key_id"]
df.loc[df["key_is_minor"], "equiv_major_key"] = (df["key_id"] - 13 + 3) % 12 + 1
df["dot_size"] = 1

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
MIN_KEY = -2
MAX_KEY = 11 + 2
df_filt = df_all[
    (df_all["key_pos_ext"] >= MIN_KEY)
    & (df_all["key_pos_ext"] <= MAX_KEY)
    & (df_all["bpm"] > 80)
    & (df_all["bpm"] <= 240)
]

df_filt = df_filt.assign(
    key_pos_jitter=(
        df_filt["key_pos_ext"] + np.random.uniform(-0.4, 0.4, size=len(df_filt))
    ),
    # jitter bpm for the very zoomed-in case:
    bpm_jitter=(
        df_filt["bpm"] + np.random.uniform(-0.02, 0.02, size=len(df_filt))
    ),
)

fig = px.scatter(
    df_filt,
    x="key_pos_jitter",
    y="bpm_jitter",
    size="dot_size",
    size_max=12,
    color="key_is_minor",
    color_discrete_map={False: "green", True: "purple"},
    custom_data=["artist", "title", "file_path"],
    labels={
        "key_pos_jitter": "Circle‑of‑Fifths Position",
        "bpm_jitter": "BPM",
        "color": "Mode",
    },
)
fig.update_traces(hovertemplate="%{customdata[1]}<br>%{customdata[0]}<extra></extra>")

key_labels = {
    1: "C<br>(Am)",
    8: "G<br>(Em)",
    3: "D<br>(Bm)",
    10: "A<br>(F#m)",
    5: "E<br>(C#m)",
    12: "B<br>(G#m)",
    7: "Gb<br>(Ebm)",
    2: "Db<br>(Bbm)",
    9: "Ab<br>(Fm)",
    4: "Eb<br>(Cm)",
    11: "Bb<br>(Gm)",
    6: "F<br>(Dm)",
}
fig.update_layout(
    xaxis={
        "tickmode": "array",
        "tickvals": list(range(MIN_KEY, MAX_KEY + 1)),
        "ticktext": [
            key_labels[circle_order[pos % 12]] for pos in range(MIN_KEY, MAX_KEY + 1)
        ],
    },
    legend={"title": "Minor"},
    title="BPM vs Circle‑of‑Fifths (interactive)",
    height=850,
)

# standalone HTML, so we can augment with "click to copy file track"
chart_div = pyo.plot(fig, include_plotlyjs="cdn", output_type="div")
output_file = Path(__file__).parent / "out" / "bpm_circle.html"
output_file.parent.mkdir(exist_ok=True, parents=True)
output_file.write_text(
    """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>BPM vs Circle-of-Fifths</title>
  </head>
  <body>
""" + chart_div + """
    <script>
      const plotDiv = document.getElementsByClassName(
        "plotly-graph-div"
      )[0];
      plotDiv.on("plotly_click", (data) => {
        const filePath = data.points[0].customdata[2];
        const fileStem = filePath
          .split("/")
          .pop()
          .split(".")
          .slice(0, -1)
          .join(".");
        navigator.clipboard
          .writeText(fileStem)
          .then(() => {
            // create a toast div
            const toast = document.createElement("div");
            toast.textContent = `Copied: ${fileStem}`;
            Object.assign(toast.style, {
              fontFamily: "sans-serif",
              position: "fixed",
              bottom: "20px",
              right: "20px",
              backgroundColor: "rgba(0,0,0,0.7)",
              color: "#fff",
              padding: "12px 20px",
              borderRadius: "6px",
              fontSize: "22px",
              zIndex: 1000,
              opacity: 0,
              transition: "opacity 0.3s",
            });
            document.body.appendChild(toast);
            // fade in
            setTimeout(() => (toast.style.opacity = 1), 10);
            // fade out and remove
            setTimeout(() => (toast.style.opacity = 0), 2000);
            setTimeout(() => document.body.removeChild(toast), 2300);
          })
          .catch((err) => console.error("Clipboard error:", err));
      });
    </script>
  </body>
</html>
""",
    encoding="UTF-8",
)
webbrowser.open(output_file.absolute().as_uri())
