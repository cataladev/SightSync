import pygame as pg
import pygame_gui
import os
import sys

# Initialize pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
pg.init()

# Screen setup
screen_width, screen_height = 600, 400
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Sight Sync")

# Initialize UI manager
manager = pygame_gui.UIManager((screen_width, screen_height))

# Colors
NAVBAR_COLOR = pg.Color(43, 177, 234)  # Blue
WHITE = pg.Color(255, 255, 255)
BLACK = pg.Color(0, 0, 0)
BG_COLOR = pg.Color(240, 245, 250)

# Font setup with Pygame CE compatibility
try:
    title_font = pg.font.SysFont("Arial", 22, bold=True)
    # Create a test surface to check font compatibility
    test_surface = title_font.render("Test", True, WHITE)
except Exception as e:
    print(f"Font error: {e}. Using fallback font.")
    title_font = pg.font.SysFont(None, 22, bold=True)

# Create UI elements with Pygame CE compatible methods
nav_title = pygame_gui.elements.UILabel(
    relative_rect=pg.Rect((10, 10), (200, 30)),
    text="Sight Sync",
    manager=manager
)
# Use text_color instead of text_colour for Pygame CE
nav_title.text_color = WHITE
nav_title.font = title_font

# Manually set the font if rebuild fails
try:
    nav_title.rebuild()
except AttributeError:
    # Fallback for Pygame CE font handling
    text_surface = title_font.render("Sight Sync", True, BLACK)
    nav_title.set_image(text_surface)

# Help button
help_button = pygame_gui.elements.UIButton(
    relative_rect=pg.Rect((screen_width-50, 10), (30, 30)),
    text="?",
    manager=manager
)

# Button styling compatible with Pygame CE
btn_states = ['normal', 'hovered', 'active']
for state in btn_states:
    setattr(help_button, f'{state}_bg_color', NAVBAR_COLOR)
    setattr(help_button, f'{state}_text_color', WHITE)
    setattr(help_button, f'{state}_border_color', WHITE)

help_button.border_width = 2
help_button.shape_corner_radius = 15  # Circular button

# Instruction label
instruction_label = pygame_gui.elements.UILabel(
    relative_rect=pg.Rect((50, 120), (screen_width-100, 80)),
    text="Say 'sync on' to start",
    manager=manager,
)
instruction_label.text_color = BLACK
instruction_label.text_horiz_alignment = "center"

# Help popup tracking
help_popup = None

def quit_game():
    """Properly clean up pygame resources"""
    pg.quit()
    sys.exit()

# Main game loop
clock = pg.time.Clock()
running = True
while running:
    time_delta = clock.tick(60)/1000.0
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit_game()
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == help_button and help_popup is None:
                help_popup = pygame_gui.windows.UIMessageWindow(
                    rect=pg.Rect((150, 150), (300, 200)),
                    html_message="<b>Help Information</b><br><br>"
                                "• Say <b>'sync on'</b> to start<br>"
                                "• Say <b>'sync off'</b> to stop<br>"
                                "• Say <b>'commands'</b> for options",
                    manager=manager,
                    window_title='Help'
                )
        
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if hasattr(event, 'ui_element') and event.ui_element == help_popup:
                help_popup = None
        
        manager.process_events(event)
    
    manager.update(time_delta)
    
    # Draw everything
    screen.fill(BG_COLOR)
    pg.draw.rect(screen, NAVBAR_COLOR, pg.Rect(0, 0, screen_width, 50))
    manager.draw_ui(screen)
    pg.display.update()

quit_game()