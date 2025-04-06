import pygame as pg
import pygame_gui
import os
import sys
import subprocess
import threading
import time
from voice import listen_and_execute, set_voice_status, get_voice_status, should_exit_app

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
pg.init()

screen_width, screen_height = 600, 400
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Sight Sync")

manager = pygame_gui.UIManager((screen_width, screen_height), 'theme.json')

NAVBAR_COLOR = pg.Color(43, 177, 234)
WHITE = pg.Color(255, 255, 255)
BG_COLOR = pg.Color(28, 37, 46)

try:
    title_font = pg.font.SysFont("Arial", 22, bold=True)
    _ = title_font.render("Test", True, WHITE)
except Exception as e:
    print(f"Font error: {e}")
    title_font = pg.font.SysFont(None, 22, bold=True)

nav_title = pygame_gui.elements.UILabel(
    relative_rect=pg.Rect((10, 10), (200, 30)),
    text="Sight Sync",
    manager=manager
)
nav_title.text_color = WHITE
nav_title.font = title_font

try:
    nav_title.rebuild()
except AttributeError:
    text_surface = title_font.render("Sight Sync", True, (0, 0, 0))
    nav_title.set_image(text_surface)

help_button = pygame_gui.elements.UIButton(
    relative_rect=pg.Rect((screen_width - 50, 10), (30, 30)),
    text="?",
    manager=manager
)
btn_states = ['normal', 'hovered', 'active']
for state in btn_states:
    setattr(help_button, f'{state}_bg_color', NAVBAR_COLOR)
    setattr(help_button, f'{state}_text_color', WHITE)
    setattr(help_button, f'{state}_border_color', WHITE)
help_button.border_width = 2
help_button.shape_corner_radius = 15

# Some instruction labels
label_width = screen_width - 100
label_height = 30
start_x = 50
start_y = 170
gap = 10

instruction_label_on = pygame_gui.elements.UILabel(
    relative_rect=pg.Rect((start_x, start_y), (label_width, label_height)),
    text="Say 'sync on' to start",
    manager=manager
)
instruction_label_off = pygame_gui.elements.UILabel(
    relative_rect=pg.Rect((start_x, start_y + label_height + gap), (label_width, label_height)),
    text="Say 'sync off' to stop",
    manager=manager
)
instruction_label_help = pygame_gui.elements.UILabel(
    relative_rect=pg.Rect((start_x, start_y + 2 * (label_height + gap)), (label_width, label_height)),
    text="Say 'help' for a list of commands",
    manager=manager
)

help_window_process = None  # Track subprocess for help window

def quit_game():
    pg.quit()
    sys.exit()

# Start voice recognition in background
voice_thread = threading.Thread(target=listen_and_execute, daemon=True)
voice_thread.start()

clock = pg.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit_game()

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == help_button:
                # Check if a help window is already running
                if help_window_process is None or help_window_process.poll() is not None:
                    # Either no process yet or the old one has exited
                    help_window_process = subprocess.Popen(["python", "help_window.py"])
                else:
                    print("Help window is already open.")

        manager.process_events(event)

    # Check for shutdown from voice manager
    if should_exit_app():
        running = False

    manager.update(time_delta)
    screen.fill(BG_COLOR)
    pg.draw.rect(screen, NAVBAR_COLOR, pg.Rect(0, 0, screen_width, 50))
    manager.draw_ui(screen)
    pg.display.update()

quit_game()
