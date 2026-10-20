
import librosa
import numpy as np


def extract_features(audio_path):
    # Load audio consistently at 16 kHz
    y, sr = librosa.load(audio_path, sr=16000, mono=True)

    if len(y) == 0:
        raise ValueError(f"Empty audio file: {audio_path}")

    # MFCC: average and variation for each of 13 coefficients
    mfcc = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=13
    )

    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    # Energy and spectral features
    rms = librosa.feature.rms(y=y)[0]
    zcr = librosa.feature.zero_crossing_rate(y=y)[0]
    centroid = librosa.feature.spectral_centroid(
        y=y, sr=sr
    )[0]

    features = np.concatenate([
        mfcc_mean,
        mfcc_std,
        [
            np.mean(rms),
            np.std(rms),
            np.mean(zcr),
            np.std(zcr),
            np.mean(centroid),
            np.std(centroid),
            len(y) / sr
        ]
    ])

    return features.astype(np.float32)
