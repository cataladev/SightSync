import pygame as pg
import pygame_gui
import sys
import os

def run_help_window():
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    pg.init()

    width, height = 450, 450
    help_screen = pg.display.set_mode((width, height))
    pg.display.set_caption("Sight Sync - Help")

    manager = pygame_gui.UIManager((width, height))

    clock = pg.time.Clock()
    running = True

    # Column layout settings (left-aligned)
    col1_x = 10
    column_width = 210
    gutter = 20
    col2_x = col1_x + column_width + gutter

    # Helper functions with reduced spacing & left alignment
    def place_heading(x, y, text):
        label = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect(x, y, column_width, 20),
            text=text,
            manager=manager
        )
        # Force left alignment and rebuild
        label.text_horiz_alignment = "left"
        label.rebuild()
        return y + 18  # slightly smaller gap after heading

    def place_bullet(x, y, text):
        label = pygame_gui.elements.UILabel(
            relative_rect=pg.Rect(x, y, column_width, 20),
            text="• " + text,
            manager=manager
        )
        # Force left alignment and rebuild
        label.text_horiz_alignment = "left"
        label.rebuild()
        return y + 14  # slightly smaller gap after bullet

    # --- Left Column: Window, Mouse ---
    col1_y = 30

    # Window
    col1_y = place_heading(col1_x, col1_y, "Window")
    col1_y = place_bullet(col1_x + 10, col1_y, "Close")
    col1_y = place_bullet(col1_x + 10, col1_y, "Kill")
    col1_y = place_bullet(col1_x + 10, col1_y, "Hold")
    col1_y = place_bullet(col1_x + 10, col1_y, "Release")
    col1_y = place_bullet(col1_x + 10, col1_y, "Switch Window")
    col1_y = place_bullet(col1_x + 10, col1_y, "Minimize/Mini")
    col1_y = place_bullet(col1_x + 10, col1_y, "Maximize/Max")
    col1_y = place_bullet(col1_x + 10, col1_y, "Fullscreen")
    col1_y = place_bullet(col1_x + 10, col1_y, "Unfullscreen")
    col1_y = place_bullet(col1_x + 10, col1_y, "Refresh")
    col1_y += 8

    # Mouse
    col1_y = place_heading(col1_x, col1_y, "Mouse")
    col1_y = place_bullet(col1_x + 10, col1_y, "Click/Press")
    col1_y = place_bullet(col1_x + 10, col1_y, "Right Click/Right Press")
    col1_y = place_bullet(col1_x + 10, col1_y, "Double Click/Double Press")
    col1_y = place_bullet(col1_x + 10, col1_y, "Scroll Up")
    col1_y = place_bullet(col1_x + 10, col1_y, "Scroll Down")
    col1_y = place_bullet(col1_x + 10, col1_y, "Scroll Left")
    col1_y = place_bullet(col1_x + 10, col1_y, "Scroll Right")
    col1_y = place_bullet(col1_x + 10, col1_y, "Zoom In")
    col1_y = place_bullet(col1_x + 10, col1_y, "Zoom Out")
    col1_y += 8

    # --- Right Column: Keyboard, Audio, Misc ---
    col2_y = 30

    # Keyboard
    col2_y = place_heading(col2_x, col2_y, "Keyboard")
    col2_y = place_bullet(col2_x + 10, col2_y, "Type")
    col2_y = place_bullet(col2_x + 10, col2_y, "Copy")
    col2_y = place_bullet(col2_x + 10, col2_y, "Paste")
    col2_y = place_bullet(col2_x + 10, col2_y, "Cut")
    col2_y = place_bullet(col2_x + 10, col2_y, "Select All")
    col2_y = place_bullet(col2_x + 10, col2_y, "Undo")
    col2_y = place_bullet(col2_x + 10, col2_y, "Redo")
    col2_y = place_bullet(col2_x + 10, col2_y, "Find")
    col2_y = place_bullet(col2_x + 10, col2_y, "Enter")
    col2_y = place_bullet(col2_x + 10, col2_y, "Save")
    col2_y = place_bullet(col2_x + 10, col2_y, "Escape")
    col2_y = place_bullet(col2_x + 10, col2_y, "Space")
    col2_y = place_bullet(col2_x + 10, col2_y, "Backspace")
    col2_y = place_bullet(col2_x + 10, col2_y, "Delete")
    col2_y = place_bullet(col2_x + 10, col2_y, "Erase Line")
    col2_y += 8

    # Audio
    col2_y = place_heading(col2_x, col2_y, "Audio")
    col2_y = place_bullet(col2_x + 10, col2_y, "Volume Up/Sound Up")
    col2_y = place_bullet(col2_x + 10, col2_y, "Volume Down/Sound Down")
    col2_y = place_bullet(col2_x + 10, col2_y, "Mute/Unmute")
    col2_y += 8

    # Misc
    col2_y = place_heading(col2_x, col2_y, "Misc")
    col2_y = place_bullet(col2_x + 10, col2_y, "Open '__'")
    col2_y = place_bullet(col2_x + 10, col2_y, "Screenshot")
    col2_y = place_bullet(col2_x + 10, col2_y, "Bright Up")
    col2_y = place_bullet(col2_x + 10, col2_y, "Bright Down")
    col2_y += 8

    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            manager.process_events(event)

        manager.update(time_delta)

        help_screen.fill((28, 37, 46))  # Background color
        manager.draw_ui(help_screen)
        pg.display.update()

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    run_help_window()
