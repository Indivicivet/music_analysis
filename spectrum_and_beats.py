from pathlib import Path

import matplotlib.pyplot as plt
import seaborn
import numpy as np
import librosa

seaborn.set()

TRACK_PATH = Path(__file__).parent / "music" / "ddhn.mp3"

timeseries, sample_rate = librosa.load(TRACK_PATH)
print(timeseries.shape)
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
plt.figure(figsize=(12.8, 7.2))
plt.plot(beat_times[:-1], bpms)
plt.xlabel("time")
plt.ylabel("bpm")
plt.show()

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
