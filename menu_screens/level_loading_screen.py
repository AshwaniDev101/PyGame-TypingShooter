import pygame
import pygame.gfxdraw
from campaign.checkpoint_manager import CheckpointManager
from config import utils
from config import constants
from config.loader import Loader
from menu_screens.gui_button import HintButton, ColorfullyButton

# Parameters for drawing dotted lines
SOLID_LINE_THICKNESS = 2
DOT_RADIUS = 1
DOT_GAP = 5

# Animation settings for hover effects
SMOOTHING = 10
HOVER_TARGET = 1.3
NORMAL_SCALE = 1.0

# Layout constants for level selection
NUM_ROWS = 3
NUM_CIRCLES = 5
CIRCLE_RADIUS = 20
CIRCLE_GAP = 20
BOSS_SIZE = 40
ROW_VERTICAL_SPACING = 120
BOSS_OFFSET = 40
BOSS_Y_SHIFT = -50
FIRST_ROW_Y_OFFSET = 150
ROW_COUNT_HEIGHT = FIRST_ROW_Y_OFFSET + (NUM_ROWS - 1) * ROW_VERTICAL_SPACING + (BOSS_SIZE // 2)
UI_TOP_MARGIN = (constants.SCREEN_HEIGHT - ROW_COUNT_HEIGHT) // 2


# Helper function to draw a dotted line between two points
def draw_dotted_line(surface, color, start, end, dot_radius=DOT_RADIUS, gap=DOT_GAP):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = (dx**2 + dy**2) ** 0.5
    if distance == 0:
        return
    dot_space = 2 * dot_radius + gap  # Space for one dot plus gap
    num_dots = int(distance / dot_space)
    step_x = dx / num_dots if num_dots else 0
    step_y = dy / num_dots if num_dots else 0
    for i in range(num_dots + 1):
        dot_center = (int(start[0] + i * step_x), int(start[1] + i * step_y))
        pygame.draw.circle(surface, color, dot_center, dot_radius)


# Unified ClickableLevel class for both level circles and boss icons.
class ClickableLevel:
    def __init__(self, center, **kwargs):
        self.center = center                 # Center coordinate
        self.color = kwargs.get("color", constants.WHITE)
        self.radius = kwargs.get("radius", CIRCLE_RADIUS)  # Base radius for circles
        self.number = kwargs.get("number", None)           # Level number to display
        self.locked = kwargs.get("is_lock", False)         # Locked status flag
        self.image = kwargs.get("image", None)             # Optional image (for boss icons)
        self.current_scale = NORMAL_SCALE                  # For hover scaling effect
        self.is_visual_only = kwargs.get("is_visual_only", False)  # Visual-only icons are non-interactive

    # Determine if mouse is hovering over this level icon (only interactive ones respond)
    def is_hovered(self, mouse_pos):
        if self.is_visual_only:
            return False
        r = int(self.radius * self.current_scale)
        x, y = self.center
        return ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2) <= r * r

    # Update the scale smoothly for hover effect
    def update(self, dt, active):
        target = HOVER_TARGET if active else NORMAL_SCALE
        self.current_scale += (target - self.current_scale) * SMOOTHING * dt

    # Draw the level icon. If an image is provided, scale and blit it; otherwise, draw a circle.
    # When active and interactive, draw a red border of thickness 5px.
    def draw(self, surface, active):
        # Calculate the scaled radius based on the current scale
        r = int(self.radius * self.current_scale)

        if active:
            # Draw a halo circle underneath by increasing the radius (e.g., by 10 pixels)
            halo_radius = r + 5
            pygame.gfxdraw.filled_circle(surface, self.center[0], self.center[1], halo_radius, utils.color("FFB34B"))

        # Draw the level icon: if an image is provided, scale and blit it; otherwise, draw a filled circle
        if self.image is not None:
            img = pygame.transform.smoothscale(self.image, (2 * r, 2 * r))
            img_rect = img.get_rect(center=self.center)
            surface.blit(img, img_rect)
        else:
            pygame.gfxdraw.filled_circle(surface, self.center[0], self.center[1], r, self.color)
            pygame.gfxdraw.aacircle(surface, self.center[0], self.center[1], r, self.color)

        # Render the level number if the level is unlocked
        if not self.locked and self.number is not None:
            font = pygame.font.Font("assets/fonts/Righteous-Regular.ttf", 20)
            text = font.render(str(self.number), True, utils.color("3C3F41"))
            text_rect = text.get_rect(center=self.center)
            surface.blit(text, text_rect)


# Main class managing level selection screen and UI
class LevelLoadingScreen:
    def __init__(self, screen, star_background):
        self.screen = screen                       # Display surface
        self.background = star_background          # Star background animation
        self.clickable_levels = []                 # List of level icons
        checkpoint_manager = CheckpointManager()
        unlocked = checkpoint_manager.get_list_of_unlocked_checkpoints()  # Get unlocked levels
        unlock_threshold = len(unlocked)
        self.setup_levels(unlock_threshold)        # Create level icons based on an unlocked threshold
        self.selected_index = 0                    # Currently selected level index
        self.should_exit = False                   # Flag to exit the level selection screen

        self.checkpoint_manager = CheckpointManager()  # Delete checkpoint when clicking delete button

        # Load navigation sound if available
        try:
            self.move_sound = Loader.load_sound("assets/sounds/menu_hover_sound.wav")
        except Exception as e:
            print("Error loading move sound:", e)
            self.move_sound = None

        # Load lock image for locked levels
        try:
            self.lock_image = utils.loader_scale_image("assets/images/level_selection_screen/lock.png", 20)
        except Exception as e:
            print("Error loading lock image:", e)
            self.lock_image = None

        # Load boss image to be used as overlay on level 5
        try:
            self.boss_img = utils.loader_scale_image("assets/images/bosses/boss_1.png", BOSS_SIZE)
        except Exception as e:
            print("Error loading boss image:", e)
            self.boss_img = None

        # Only interactive levels (non-visual-only) are selectable
        self.selectable_levels = [s for s in self.clickable_levels if not s.is_visual_only]
        self.setup_buttons()  # Create UI buttons

    # Create UI buttons for controls and the Delete function
    def setup_buttons(self):
        control_font = pygame.font.Font(pygame.font.match_font("arial"), 15)
        self.buttons = {}
        self.buttons['esc'] = HintButton("ESC", (10, 10), control_font, can_hover=True)
        control_y = constants.SCREEN_HEIGHT - 100
        self.buttons['enter'] = HintButton("Enter", (60, control_y - 30), control_font)
        self.buttons['space'] = HintButton("Space", (60, control_y + 5), control_font)
        left_arrow_x = constants.SCREEN_WIDTH - 200
        self.buttons['left_arrow'] = HintButton("Left Arrow", (left_arrow_x, control_y - 10), control_font)
        right_arrow_text = "Right Arrow"
        right_arrow_width = control_font.size(right_arrow_text)[0] + 15 * 2
        right_arrow_x = constants.SCREEN_WIDTH - right_arrow_width - 10
        self.buttons['right_arrow'] = HintButton(right_arrow_text, (right_arrow_x, control_y - 10), control_font)
        self.buttons['delete'] = ColorfullyButton("Delete Saves", (constants.SCREEN_WIDTH - 140, 10), control_font,
                                                  height=50,
                                                  prefix_image_path="assets/images/level_selection_screen/dustbin.png")
        self.control_font = control_font

    # Setup level icons (circles) using images if available.
    def setup_levels(self, unlock_threshold):
        total_circles_width = NUM_CIRCLES * (2 * CIRCLE_RADIUS) + (NUM_CIRCLES - 1) * CIRCLE_GAP
        row_width = total_circles_width + BOSS_OFFSET + BOSS_SIZE
        for row in range(NUM_ROWS):
            row_y = UI_TOP_MARGIN + FIRST_ROW_Y_OFFSET + row * ROW_VERTICAL_SPACING
            horizontal_offset = row * (2 * CIRCLE_RADIUS)
            start_x = (self.screen.get_width() - row_width) // 2 + horizontal_offset
            for j in range(NUM_CIRCLES):
                cx = start_x + j * (2 * CIRCLE_RADIUS + CIRCLE_GAP) + CIRCLE_RADIUS
                level_num = row * NUM_CIRCLES + j + 1
                locked = level_num > unlock_threshold
                self.clickable_levels.append(
                    ClickableLevel((cx, row_y),
                                   radius=CIRCLE_RADIUS,
                                   number=level_num,
                                   is_lock=locked)
                )
            # Boss icons removed

    # Handle mouse motion, clicks, and key presses.
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                for btn in self.buttons.values():
                    btn.update_hover(mouse_pos)
                self.handle_mouse_motion(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.buttons['esc'].rect.collidepoint(pos):
                    self.should_exit = True
                    return "Escape"
                if self.buttons['delete'].rect.collidepoint(pos):
                    self.delete_save_files()
                    return "Escape"
                else:
                    for i, level in enumerate(self.selectable_levels):
                        if level.is_hovered(pos):
                            self.update_selection(i)
                            return self.summit(self.selectable_levels[self.selected_index])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Escape"
                elif event.key == pygame.K_LEFT:
                    new_index = (self.selected_index - 1) % len(self.selectable_levels)
                    self.update_selection(new_index)
                elif event.key == pygame.K_RIGHT:
                    new_index = (self.selected_index + 1) % len(self.selectable_levels)
                    self.update_selection(new_index)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.summit(self.selectable_levels[self.selected_index])

    # Update the selected level index and play sound if changed.
    def update_selection(self, new_index):
        if new_index != self.selected_index:
            self.selected_index = new_index
            if self.move_sound:
                self.move_sound.play()

    # Update selection based on mouse hover.
    def handle_mouse_motion(self, mouse_pos):
        for i, level in enumerate(self.selectable_levels):
            if level.is_hovered(mouse_pos):
                if i != self.selected_index:
                    self.update_selection(i)
                break

    # Update all interactive elements based on the time delta.
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for level in self.clickable_levels:
            active = level.is_hovered(mouse_pos) or (level in self.selectable_levels and level == self.selectable_levels[self.selected_index])
            level.update(dt, active)

    # Draw the entire level selection screen, including background, levels, and UI buttons.
    def draw(self):
        self.screen.fill(constants.BLACK)
        t = pygame.time.get_ticks()
        self.background.update_and_draw(self.screen, t)

        if len(self.selectable_levels) >= 15:
            pygame.draw.line(self.screen, constants.WHITE, self.selectable_levels[0].center, self.selectable_levels[4].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, constants.WHITE, self.selectable_levels[4].center, self.selectable_levels[5].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, constants.WHITE, self.selectable_levels[5].center, self.selectable_levels[9].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, constants.WHITE, self.selectable_levels[9].center, self.selectable_levels[10].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, constants.WHITE, self.selectable_levels[10].center, self.selectable_levels[14].center, SOLID_LINE_THICKNESS)
            # Dotted lines removed

        mouse_pos = pygame.mouse.get_pos()
        for level in self.clickable_levels:
            active = level.is_hovered(mouse_pos) or (level in self.selectable_levels and level == self.selectable_levels[self.selected_index])
            level.draw(self.screen, active)
            # For circle with number 5, overlay the boss image with an offset (x + 100, y - 100)
            if level.number == 15 and self.boss_img is not None:
                boss_rect = self.boss_img.get_rect()
                boss_rect.topleft = (level.center[0] + 30, level.center[1] - 20)
                self.screen.blit(self.boss_img, boss_rect)
            # Overlay lock image if level is locked and no image is provided
            if not level.is_visual_only and level.image is None and level.locked and self.lock_image is not None:
                lock_rect = self.lock_image.get_rect(center=level.center)
                self.screen.blit(self.lock_image, lock_rect)

        for btn in self.buttons.values():
            btn.draw(self.screen)
        control_y = constants.SCREEN_HEIGHT - 100
        select_text = self.control_font.render("Select", True, constants.WHITE)
        select_rect = select_text.get_rect(midleft=(20, control_y))
        self.screen.blit(select_text, select_rect)
        pygame.display.flip()

    # Confirm level selection; if unlocked, return its number.
    def summit(self, clickable_level: ClickableLevel):
        if not clickable_level.locked:
            return {"Level-Selected": clickable_level.number}
        return {"Level-Selected": None}

    def delete_save_files(self):
        self.checkpoint_manager.delete_all_except_checkpoint_1()
        print("delete button clicked")
#
# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
#     pygame.display.set_caption("Level Selection Screen")
#     clock = pygame.time.Clock()
#     star_bg = StarBackground()
#     level_screen = LevelLoadingScreen(screen, star_bg)
#     running = True
#     while running:
#         dt = clock.tick(FPS) / 1000.0  # Delta time for smooth animations
#         events = pygame.event.get()
#         for event in events:
#             if event.type == pygame.QUIT:
#                 running = False
#         result = level_screen.handle_events(events)
#         if result == "Escape" or level_screen.should_exit:
#             running = False
#         level_screen.update(dt)
#         level_screen.draw()
#     pygame.quit()
#
# if __name__ == "__main__":
#     main()
