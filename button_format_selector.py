# button_format_selector.py

# --- Encargado de gestionar que formato va a utilizar ---

import pygame
from config import COLOR_TEXT, SCREEN_WIDTH

# Pregunta que formato va a utilizar
#
def choose_button_format(screen):
    # Declara el texto y la fuente
    font = pygame.font.SysFont(None, 28)
    prompt = "Selecciona el formato de botones:"
    option1 = "Presiona [4] para 4 botones"
    option2 = "Presiona [6] para 6 botones"

    choosing = True
    while choosing:
        # Dibuja el texto y lo posiciona en el recuadro
        screen.fill((0, 0, 0))
        draw_centered_text(screen, font, prompt, y=25)
        draw_centered_text(screen, font, option1, y=80)
        draw_centered_text(screen, font, option2, y=125)
        pygame.display.flip()

        for event in pygame.event.get():
            # Detecta el formato a utilizar o quita el programa con ayuda del foco o con la tecla Esc
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4:
                    return 4
                elif event.key == pygame.K_6:
                    return 6
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

def draw_centered_text(screen, font, text, y):
    surface = font.render(text, True, COLOR_TEXT)
    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surface, rect)

