import pygame
import pygame.gfxdraw

from campaign_manager.checkpoint_manager import CheckpointManager
from config import utils
from config import constants
from config.loader import Loader
from menu_screens.gui_button import HintButton, ColorfullyButton


# --- Constants ---
SOLID_LINE_THICKNESS = 3
DOT_RADIUS = 2
DOT_GAP = 6

SMOOTHING = 12
HOVER_TARGET = 1.35
NORMAL_SCALE = 1.0

NUM_ROWS = 2
NUM_CIRCLES = 5
CIRCLE_RADIUS = 24
CIRCLE_GAP = 50
ROW_VERTICAL_SPACING = 130
FIRST_ROW_Y_OFFSET = 180
UI_TOP_MARGIN = (constants.SCREEN_HEIGHT - (FIRST_ROW_Y_OFFSET + (NUM_ROWS-1)*ROW_VERTICAL_SPACING + 80)) // 2


# Helper: Draw smooth dotted line
def draw_dotted_line(surface, color, start, end, dot_radius=DOT_RADIUS, gap=DOT_GAP):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = (dx**2 + dy**2) ** 0.5
    if distance == 0:
        return
    dot_space = 2 * dot_radius + gap
    num_dots = int(distance / dot_space) + 1
    step_x = dx / num_dots if num_dots else 0
    step_y = dy / num_dots if num_dots else 0
    for i in range(num_dots + 1):
        dot_center = (int(start[0] + i * step_x), int(start[1] + i * step_y))
        pygame.draw.circle(surface, color, dot_center, dot_radius)


# Clickable level icon
class ClickableLevel:
    def __init__(self, center, **kwargs):
        self.center = center
        self.color = kwargs.get("color", constants.WHITE)
        self.radius = kwargs.get("radius", CIRCLE_RADIUS)
        self.number = kwargs.get("number", None)
        self.locked = kwargs.get("locked", False)
        self.image = kwargs.get("image", None)
        self.current_scale = NORMAL_SCALE
        self.is_visual_only = kwargs.get("is_visual_only", False)

    def is_hovered(self, mouse_pos):
        if self.is_visual_only:
            return False
        r = int(self.radius * self.current_scale)
        x, y = self.center
        return ((mouse_pos[0] - x)**2 + (mouse_pos[1] - y)**2) <= r * r

    def update(self, dt, active):
        target = HOVER_TARGET if active else NORMAL_SCALE
        self.current_scale += (target - self.current_scale) * SMOOTHING * dt

    def draw(self, surface, active):
        r = int(self.radius * self.current_scale)

        # Smooth halo glow
        halo_r = r + (15 if active and self.current_scale > 1.1 else 8)
        halo_color = utils.color("FFB34B") if active else (40, 40, 40)
        pygame.gfxdraw.filled_circle(surface, *self.center, halo_r, halo_color)
        pygame.gfxdraw.filled_circle(surface, *self.center, halo_r - 4, (0, 0, 0))

        # Thick border when selected
        border_color = utils.color("FF4D66") if active and self.current_scale > 1.1 else utils.color("FFB34B")
        border_r = r + 4
        pygame.gfxdraw.aacircle(surface, *self.center, border_r, border_color)
        pygame.gfxdraw.aacircle(surface, *self.center, border_r - 1, border_color)

        # Main circle
        pygame.gfxdraw.filled_circle(surface, *self.center, r, self.color)
        pygame.gfxdraw.aacircle(surface, *self.center, r, self.color)

        # Level number
        if not self.locked and self.number:
            font = Loader.load_font("assets/fonts/Righteous-Regular.ttf", 24)
            text = font.render(str(self.number), True, (20, 20, 20))
            text_rect = text.get_rect(center=self.center)
            surface.blit(text, text_rect)

        # Lock overlay
        if self.locked and hasattr(self, 'lock_image') and self.lock_image:
            lock_rect = self.lock_image.get_rect(center=self.center)
            surface.blit(self.lock_image, lock_rect)


# Main level selection screen
class LevelLoadingScreen:
    def __init__(self, screen, star_background):
        self.screen = screen
        self.background = star_background
        self.clickable_levels = []
        self.selected_index = 0
        self.should_exit = False

        self.checkpoint_manager = CheckpointManager()
        unlocked = self.checkpoint_manager.get_list_of_unlocked_checkpoints()
        unlock_threshold = max(unlocked) if unlocked else 0

        self.setup_levels(unlock_threshold)
        self.selectable_levels = [s for s in self.clickable_levels if not s.is_visual_only]

        # Load assets
        try:
            self.move_sound = Loader.load_sound("assets/sounds/menu_hover_sound.wav")
        except:
            self.move_sound = None

        try:
            self.lock_image = utils.loader_scale_image("assets/images/level_selection_screen/lock.png", 30)
        except:
            self.lock_image = None

        for level in self.clickable_levels:
            level.lock_image = self.lock_image

        try:
            self.boss_img = utils.loader_scale_image("assets/images/bosses/boss_1.png", 70)
        except:
            self.boss_img = None

        self.setup_buttons()

    def setup_levels(self, unlock_threshold):
        row_width = NUM_CIRCLES * (2 * CIRCLE_RADIUS + CIRCLE_GAP) - CIRCLE_GAP
        for row in range(NUM_ROWS):
            row_y = UI_TOP_MARGIN + FIRST_ROW_Y_OFFSET + row * ROW_VERTICAL_SPACING
            start_x = (self.screen.get_width() - row_width) // 2
            for j in range(NUM_CIRCLES):
                cx = start_x + j * (2 * CIRCLE_RADIUS + CIRCLE_GAP) + CIRCLE_RADIUS
                level_num = row * NUM_CIRCLES + j + 1
                locked = level_num > unlock_threshold
                self.clickable_levels.append(
                    ClickableLevel((cx, row_y), number=level_num, locked=locked)
                )

    def setup_buttons(self):
        font = pygame.font.SysFont("arial", 16, bold=True)
        small_font = pygame.font.SysFont("arial", 14)

        self.buttons = {}

        # Top-left back button
        self.buttons['esc'] = HintButton("Back (Esc)", (15, 15), font, can_hover=True)

        # Bottom-left: Space + (Select)
        left_control_y = constants.SCREEN_HEIGHT - 100
        self.buttons['space'] = HintButton("Space", (70, left_control_y - 10), font)

        # "(Select)" label under Space
        self.select_label = small_font.render("(Select)", True, constants.WHITE)

        # Bottom-right: Arrow keys
        arrow_base_x = constants.SCREEN_WIDTH - 220
        arrow_y = constants.SCREEN_HEIGHT - 120

        self.buttons['up_arrow'] = HintButton("↑", (arrow_base_x + 60, arrow_y - 40), font)
        self.buttons['left_arrow'] = HintButton("←", (arrow_base_x, arrow_y), font)
        self.buttons['right_arrow'] = HintButton("→", (arrow_base_x + 120, arrow_y), font)
        self.buttons['down_arrow'] = HintButton("↓", (arrow_base_x + 60, arrow_y), font)

        # "(Navigate)" label under the arrow group
        self.navigate_label = small_font.render("(Navigate)", True, constants.WHITE)

        # Delete saves - top right
        self.buttons['delete'] = ColorfullyButton(
            "Delete Saves",
            (constants.SCREEN_WIDTH - 180, 15),
            font,
            height=50,
            prefix_image_path="assets/images/level_selection_screen/dustbin.png"
        )

    def handle_events(self, events):
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

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
                for i, level in enumerate(self.selectable_levels):
                    if level.is_hovered(pos):
                        self.update_selection(i)
                        return self.summit(self.selectable_levels[self.selected_index])

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Escape"

                current_row = self.selected_index // NUM_CIRCLES
                current_col = self.selected_index % NUM_CIRCLES

                if event.key == pygame.K_LEFT:
                    new_col = max(0, current_col - 1)
                    new_index = current_row * NUM_CIRCLES + new_col
                    self.update_selection(new_index)

                elif event.key == pygame.K_RIGHT:
                    new_col = min(NUM_CIRCLES - 1, current_col + 1)
                    new_index = current_row * NUM_CIRCLES + new_col
                    self.update_selection(new_index)

                elif event.key == pygame.K_UP:
                    new_row = max(0, current_row - 1)
                    new_index = new_row * NUM_CIRCLES + current_col
                    if new_index < len(self.selectable_levels):
                        self.update_selection(new_index)

                elif event.key == pygame.K_DOWN:
                    new_row = min(NUM_ROWS - 1, current_row + 1)
                    new_index = new_row * NUM_CIRCLES + current_col
                    if new_index < len(self.selectable_levels):
                        self.update_selection(new_index)

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.summit(self.selectable_levels[self.selected_index])

        return None

    def handle_mouse_motion(self, mouse_pos):
        for i, level in enumerate(self.selectable_levels):
            if level.is_hovered(mouse_pos) and i != self.selected_index:
                self.update_selection(i)
                break

    def update_selection(self, new_index):
        if new_index != self.selected_index:
            self.selected_index = new_index
            if self.move_sound:
                self.move_sound.play()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for level in self.clickable_levels:
            active = level.is_hovered(mouse_pos) or (level in self.selectable_levels and level == self.selectable_levels[self.selected_index])
            level.update(dt, active)

    def draw(self):
        self.screen.fill(constants.BLACK)
        t = pygame.time.get_ticks()
        self.background.update_and_draw(self.screen, t)

        # Dotted connecting lines
        if self.clickable_levels:
            levels = self.clickable_levels
            for i in range(4):
                draw_dotted_line(self.screen, constants.WHITE, levels[i].center, levels[i+1].center)
            draw_dotted_line(self.screen, constants.WHITE, levels[4].center, levels[5].center)
            for i in range(5, 9):
                draw_dotted_line(self.screen, constants.WHITE, levels[i].center, levels[i+1].center)

        # Draw levels
        mouse_pos = pygame.mouse.get_pos()
        for level in self.clickable_levels:
            active = level.is_hovered(mouse_pos) or (level in self.selectable_levels and level == self.selectable_levels[self.selected_index])
            level.draw(self.screen, active)

        # Boss image to the right of level 10
        if len(self.clickable_levels) >= 10 and self.boss_img:
            level_10 = self.clickable_levels[9]
            boss_rect = self.boss_img.get_rect()
            boss_rect.midleft = (level_10.center[0] + level_10.radius + 20, level_10.center[1])
            self.screen.blit(self.boss_img, boss_rect)

        # Draw buttons
        for btn in self.buttons.values():
            btn.draw(self.screen)

        # "(Select)" text under Space hint (bottom-left)
        select_label_rect = self.select_label.get_rect()
        select_label_rect.centerx = self.buttons['space'].rect.centerx
        select_label_rect.top = self.buttons['space'].rect.bottom + 5
        self.screen.blit(self.select_label, select_label_rect)
        self.screen.blit(self.select_label, select_label_rect)

        # "(Navigate)" text under the arrow key group (bottom-right)
        navigate_label_rect = self.navigate_label.get_rect()
        navigate_label_rect.centerx = self.buttons['down_arrow'].rect.centerx
        navigate_label_rect.top = self.buttons['down_arrow'].rect.bottom + 5
        self.screen.blit(self.navigate_label, navigate_label_rect)

        pygame.display.flip()

    def summit(self, level):
        if not level.locked:
            return {"Level-Selected": level.number}
        return {"Level-Selected": None}

    def delete_save_files(self):
        self.checkpoint_manager.delete_all_except_checkpoint_1()
        print("Save files deleted (except checkpoint 1)")