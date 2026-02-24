# main.py

import pygame
import numpy as np
import threading
import uuid

from .config import *
from .audio import start_audio, audio_queue, current_volume, get_current_volume
from .network import send_audio
from .visual import draw_wave,draw_wave_layer


def main():
    global current_volume
    global unique_id

    unique_id = uuid.uuid4().hex[:12]
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("FRIDA")

    clock = pygame.time.Clock()
    stream = start_audio()

    font = pygame.font.SysFont("Arial", 28)

    recording = []
    is_recording = False
    silence_time = 0
    is_processing = False
    t = 0

    state = {"is_processing": False}

    while True:
        clock.tick(60)
        t += 0.05

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stream.stop()
                pygame.quit()
                return

        screen.fill((25, 0, 50))

        if not audio_queue.empty():
            data = audio_queue.get()
            current_volume = get_current_volume()

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

                    is_processing = True

                    def process():
                        send_audio(audio_data,unique_id)
                        nonlocal is_processing
                        is_processing = False

                    threading.Thread(target=process, daemon=True).start()

        #draw_wave(screen, current_volume * 5, t)
        draw_wave_layer(screen, current_volume * 5, t, (0, 255, 255), 0)
        draw_wave_layer(screen, current_volume * 5, t, (255, 0, 200), 0.5)
        draw_wave_layer(screen, current_volume * 5, t, (100, 100, 255), 1)
        
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