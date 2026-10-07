import librosa
import numpy as np
import tempfile
import os


def extract_audio_features(
    audio_bytes: bytes
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_file:

        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:

        y, sr = librosa.load(
            temp_path,
            sr=None
        )

        mfcc = librosa.feature.mfcc(
            y=y,
            sr=sr,
            n_mfcc=13
        )

        mfcc_mean = np.mean(
            mfcc,
            axis=1
        )

        rms = librosa.feature.rms(y=y)
        rms_mean = np.mean(rms)

        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)

        spectral_centroid = (
            librosa.feature.spectral_centroid(
                y=y,
                sr=sr
            )
        )

        spectral_centroid_mean = np.mean(
            spectral_centroid
        )

        f0 = librosa.yin(
            y,
            fmin=50,
            fmax=500,
            sr=sr
        )

        pitch_mean = np.mean(f0)
        pitch_std = np.std(f0)

        return {
            "mfcc": mfcc_mean.tolist(),
            "rms_energy": float(rms_mean),
            "zero_crossing_rate": float(zcr_mean),
            "spectral_centroid": float(
                spectral_centroid_mean
            ),
            "pitch_mean": float(pitch_mean),
            "pitch_variation": float(pitch_std)
        }

    finally:
        os.remove(temp_path)