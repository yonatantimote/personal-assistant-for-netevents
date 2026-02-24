# network.py

import requests
import soundfile as sf
import io
from .config import SAMPLE_RATE, ENDPOINT
from .audio import play_audio

def send_audio(audio_data,unique_id):
    try:
        temp_buffer = io.BytesIO()
        sf.write(temp_buffer, audio_data, SAMPLE_RATE, format='WAV')
        temp_buffer.seek(0)

        files = {
            'file': ('audio.wav', temp_buffer, 'audio/wav')
        }

        data = {
            'request_id': unique_id
        }

        response = requests.post(ENDPOINT, files=files, data=data)

        print("ID enviado:", unique_id)

        if response.status_code == 200:
            play_audio(response.content)

    except Exception as e:
        print("Error:", e)