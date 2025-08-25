# utils.py

# --- Configuraciones que se repiten ---

import pygame
from config import COLOR_TEXT, SCREEN_WIDTH

def draw_centered_text(screen, font, text, y):
    surface = font.render(text, True, COLOR_TEXT)
    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surface, rect)

def show_error_and_exit(screen, message):
    # Muestra un mensaje de error en pantalla y espera a que el usuario salga.
    font = pygame.font.SysFont(None, 28)
    
    # Separa el mensaje en líneas si contiene saltos de línea (\n)
    error_lines = message.split('\n')
    
    running = True
    while running:
        screen.fill((20, 0, 0)) # Fondo rojo oscuro para indicar error

        # Dibuja cada línea del mensaje
        for i, line in enumerate(error_lines):
            draw_centered_text(screen, font, line, y=50 + i * 40)
        
        draw_centered_text(screen, font, "Presiona cualquier tecla para salir", y=150)

        pygame.display.flip()
        
        # Cierra la ventana con ayuda del foco o de la tecla Esc
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
            elif event.type == pygame.K_ESCAPE:
                running = False

    
    pygame.quit()
    exit()
