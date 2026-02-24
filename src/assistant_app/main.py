import pygame
import sounddevice as sd
import numpy as np
import requests
import soundfile as sf
import threading
import queue
import math
import tempfile
import io

# =========================
# Configuración
# =========================
WIDTH, HEIGHT = 1000, 500
CENTER_Y = HEIGHT // 2
THRESHOLD = 0.02
SILENCE_LIMIT = 1.0  # segundos de silencio para cortar grabación
SAMPLE_RATE = 44100

ENDPOINT = "https://n8n-consorcio-mys.noos.digital/webhook/audio-ai-agent"

current_volume = 0.0
audio_queue = queue.Queue()
recording = []
is_recording = False
silence_time = 0
is_processing = False


# =========================
# Audio callback
# =========================
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


# =========================
# Enviar audio al endpoint
# =========================
def send_audio(audio_data):
    global is_processing

    try:
        is_processing = True

        temp_buffer = io.BytesIO()
        sf.write(temp_buffer, audio_data, SAMPLE_RATE, format='WAV')
        temp_buffer.seek(0)

        files = {
            'file': ('audio.wav', temp_buffer, 'audio/wav')
        }

        response = requests.post(ENDPOINT, files=files)

        if response.status_code == 200:
            play_audio(response.content)

    except Exception as e:
        print("Error:", e)

    is_processing = False


# =========================
# Reproducir audio respuesta
# =========================
def play_audio(audio_bytes):
    data, samplerate = sf.read(io.BytesIO(audio_bytes))
    sd.play(data, samplerate)
    sd.wait()


# =========================
# Dibujar onda estilo moderno
# =========================
def draw_wave(surface, volume, t):
    points = []
    for x in range(WIDTH):
        angle = (x / WIDTH) * 8 * math.pi
        y = CENTER_Y + math.sin(angle + t) * volume * 400
        points.append((x, y))

    pygame.draw.aalines(surface, (0, 255, 200), False, points, 2)


# =========================
# Main
# =========================
def main():
    global is_recording, recording, silence_time

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Voice Assistant")

    clock = pygame.time.Clock()
    stream = start_audio()

    font = pygame.font.SysFont("Arial", 28)
    t = 0

    while True:
        clock.tick(60)
        t += 0.05

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stream.stop()
                pygame.quit()
                return

        screen.fill((25, 0, 50))

        # =========================
        # Lógica de grabación
        # =========================
        if not audio_queue.empty():
            data = audio_queue.get()

            if current_volume > THRESHOLD and not is_processing:
                is_recording = True
                silence_time = 0
                recording.append(data)

            elif is_recording:
                silence_time += 1/60
                recording.append(data)

                if silence_time > SILENCE_LIMIT:
                    is_recording = False
                    audio_data = np.concatenate(recording)
                    recording = []

                    threading.Thread(
                        target=send_audio,
                        args=(audio_data,),
                        daemon=True
                    ).start()

        # =========================
        # Visual
        # =========================
        draw_wave(screen, current_volume * 5, t)

        if is_processing:
            status = "Procesando..."
            color = (255, 200, 0)
        elif is_recording:
            status = "Escuchando..."
            color = (0, 255, 180)
        else:
            status = "En espera..."
            color = (150, 150, 150)

        text_surface = font.render(status, True, color)
        screen.blit(text_surface, (20, HEIGHT - 40))

        pygame.display.flip()


if __name__ == "__main__":
    main()