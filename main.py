import pygame
import threading
import sys
import time
from voice import listen_and_execute, set_voice_status, get_voice_status, should_exit_app


# Init Pygame
pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SightSync")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
font = pygame.font.SysFont("arial", 28)
status_font = pygame.font.SysFont("arial", 20)

# Load logo
try:
    logo = pygame.image.load("SightSync.png")
    logo = pygame.transform.scale(logo, (150, 150))
except pygame.error as e:
    print(f"[!] Could not load logo: {e}")
    logo = None

# Start voice recognition in background
voice_thread = threading.Thread(target=listen_and_execute, daemon=True)
voice_thread.start()

# Animation setup
pulse = 0
pulse_direction = 1

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    # Animate logo pulsing
    pulse += pulse_direction * 0.5
    if pulse > 10 or pulse < -10:
        pulse_direction *= -1

    if logo:
        logo_scaled = pygame.transform.scale(logo, (150 + int(pulse), 150 + int(pulse)))
        logo_rect = logo_scaled.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(logo_scaled, logo_rect)

    main_text = font.render("Say 'sync on' to start", True, BLACK)
    status_text = status_font.render(f"Status: {get_voice_status()}", True, (80, 80, 80))

    screen.blit(main_text, main_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))
    screen.blit(status_text, (10, HEIGHT - 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 🔁 Check for shutdown from voice manager
    if should_exit_app():
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


pygame.quit()
sys.exit()
