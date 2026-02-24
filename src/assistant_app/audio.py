# audio.py

import sounddevice as sd
import numpy as np
import soundfile as sf
import io
import queue
from .config import SAMPLE_RATE

audio_queue = queue.Queue()
current_volume = 0.0


def audio_callback(indata, frames, time_info, status):
    global current_volume
    volume = np.sqrt(np.mean(indata**2))
    current_volume = volume
    audio_queue.put(indata.copy())


def start_audio():
    stream = sd.InputStream(
        channels=1,
        samplerate=SAMPLE_RATE,
        callback=audio_callback
    )
    stream.start()
    return stream


def play_audio(audio_bytes):
    data, samplerate = sf.read(io.BytesIO(audio_bytes))
    sd.play(data, samplerate)
    sd.wait()

def get_current_volume():
    global current_volume
    return current_volume