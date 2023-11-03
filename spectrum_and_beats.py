from pathlib import Path

import matplotlib.pyplot as plt
import seaborn
import numpy as np
from scipy import interpolate
import librosa

seaborn.set()


def make_plot(track_path, save_name=None, show_spectrogram=False):
    timeseries, sample_rate = librosa.load(track_path)
    print(timeseries.shape, f"{sample_rate=}")
    onset_env = librosa.onset.onset_strength(
        y=timeseries,
        sr=sample_rate,
    )
    times = librosa.times_like(onset_env, sr=sample_rate)

    WINDOW = 7  # samples
    onset_spikes = onset_env * (onset_env > (onset_env.mean() * 1.2))
    beat_times = []
    for i, (t, val) in enumerate(zip(times, onset_spikes)):
        if val and val == onset_spikes[i - WINDOW:i + WINDOW].max():
            beat_times.append(t)

    deltas = np.array([b - a for a, b in zip(beat_times, beat_times[1:])])
    bpms = 60 / deltas

    bpms_smooth = interpolate.UnivariateSpline(
        beat_times[:-1],
        bpms,
        ext="const",
        k=2,
        s=500 * len(bpms),
    )(times)

    plt.figure(figsize=(19.2, 10.8))
    plt.plot(beat_times[:-1], bpms, label="detected bpms", alpha=0.2)
    plt.plot(times, bpms_smooth, label="detected bpms (smoothed)")
    plt.xlabel("time")
    plt.ylabel("bpm")
    plt.legend()
    if save_name is None:
        plt.show()
    else:
        plt.savefig(save_name)
    if not show_spectrogram:
        return
    plt.plot(times, 4000 * onset_spikes)
    mel_spectrogram = librosa.feature.melspectrogram(
        y=timeseries,
        sr=sample_rate,
        hop_length=512,
    )
    librosa.display.specshow(
        librosa.power_to_db(mel_spectrogram),
        y_axis="mel",
        x_axis="time",
        hop_length=512,
    )
    plt.show()


FOLDER = Path(__file__).parent / "working_io"
for p in FOLDER.glob("*.mp3"):
    try:
        make_plot(p, save_name=p.with_name(f"{p.stem}_bpm_plot.png"))
    except Exception as e:
        print(f"EXCEPTION: file {p}: {e!r}")
