import matplotlib.pyplot as plt
import librosa

timeseries, sample_rate = librosa.load(librosa.ex("choice"), duration=10)
print(timeseries.shape)
onset_env = librosa.onset.onset_strength(
    y=timeseries,
    sr=sample_rate,
)
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
