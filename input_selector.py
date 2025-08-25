# input_selector.py

# --- Pregunta por el metodo de entrada ---

from utils import draw_centered_text
import pygame
from config import COLOR_TEXT, SCREEN_WIDTH, SCREEN_HEIGHT

# Pregunta que metodo de entrada va a utilizar

def choose_input_mode(screen):
    # Define la fuente y el texto
    font = pygame.font.SysFont(None, 28)
    prompt = "Selecciona el modo de entrada:"
    option1 = "Presiona [T] para TECLADO"
    option2 = "Presiona [J] para JOYSTICK"

    choosing = True
    while choosing:
        # Se encarga de acomodar el texto
        screen.fill((0, 0, 0))
        draw_centered_text(screen, font, prompt, y=25)
        draw_centered_text(screen, font, option1, y=80)
        draw_centered_text(screen, font, option2, y=120)
        pygame.display.flip()

        # Cierra la ventana con ayuda del foco o con Esc, tambien determina el metodo de entrada
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_t:
                    return "teclado"
                elif event.key == pygame.K_j:
                    return "joystick"
