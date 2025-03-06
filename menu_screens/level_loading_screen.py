import pygame
import pygame.gfxdraw
from config import utils
from effects.stars import StarBackground

# Screen and FPS constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 1000
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
# Use white for connecting lines
LINE_COLOR = WHITE

# Line parameters
SOLID_LINE_THICKNESS = 2  # Solid line thickness
DOT_RADIUS = 1             # Dot radius for dotted lines
DOT_GAP = 5                # Gap between dots

# Animation parameters
SMOOTHING = 10
HOVER_TARGET = 1.3
NORMAL_SCALE = 1.0

# Layout constants for level selection
NUM_ROWS = 3
NUM_CIRCLES = 5
CIRCLE_RADIUS = 20       # Base circle radius for levels
CIRCLE_GAP = 20          # Gap between circles
BOSS_SIZE = 40           # Boss image size (reduced)
ROW_VERTICAL_SPACING = 120
BOSS_OFFSET = 40         # Gap between circles and boss image
UNLOCK_THRESHOLD = 8     # Levels greater than this are locked
BOSS_Y_SHIFT = -50       # Shift boss images upward by 50px

# UI centering: compute top margin to center rows
FIRST_ROW_Y_OFFSET = 150
ROW_COUNT_HEIGHT = FIRST_ROW_Y_OFFSET + (NUM_ROWS - 1) * ROW_VERTICAL_SPACING + (BOSS_SIZE // 2)
UI_TOP_MARGIN = (SCREEN_HEIGHT - ROW_COUNT_HEIGHT) // 2

# Button theme constants
BTN_PADDING_X = 15
BTN_HEIGHT = 30
BTN_ALPHA = 150
BTN_BORDER_RADIUS = 5

# Helper function to draw dotted line
def draw_dotted_line(surface, color, start, end, dot_radius=DOT_RADIUS, gap=DOT_GAP):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = (dx**2 + dy**2) ** 0.5
    if distance == 0:
        return
    dot_space = 2 * dot_radius + gap
    num_dots = int(distance / dot_space)
    step_x = dx / num_dots if num_dots else 0
    step_y = dy / num_dots if num_dots else 0
    for i in range(num_dots + 1):
        dot_center = (int(start[0] + i * step_x), int(start[1] + i * step_y))
        pygame.draw.circle(surface, color, dot_center, dot_radius)

# Class representing a level circle or boss square
class ClickableShape:
    def __init__(self, shape_type, center, **kwargs):
        self.shape_type = shape_type  # "circle" or "square"
        self.center = center
        self.color = kwargs.get("color", WHITE)
        self.size = kwargs.get("size", BOSS_SIZE)   # For squares
        self.radius = kwargs.get("radius", CIRCLE_RADIUS)  # For circles
        self.number = kwargs.get("number", None)
        self.is_lock = kwargs.get("is_lock", False)
        self.image = kwargs.get("image", None)
        self.current_scale = NORMAL_SCALE
        self.is_visual_only = kwargs.get("is_visual_only", False)  # Boss images are visual-only

    def is_hovered(self, mouse_pos):
        if self.is_visual_only:
            return False
        if self.shape_type == "square":
            half = int((self.size * self.current_scale) / 2)
            x, y = self.center
            rect = pygame.Rect(x - half, y - half, 2 * half, 2 * half)
            return rect.collidepoint(mouse_pos)
        else:
            r = int(self.radius * self.current_scale)
            x, y = self.center
            return ((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2) <= r * r

    def update(self, dt, active):
        if self.is_visual_only:
            self.current_scale = NORMAL_SCALE
            return
        target = HOVER_TARGET if active else NORMAL_SCALE
        self.current_scale += (target - self.current_scale) * SMOOTHING * dt

    def draw(self, surface, active):
        if self.shape_type == "square":
            scaled_size = int(self.size * self.current_scale)
            half = scaled_size // 2
            rect = pygame.Rect(self.center[0] - half, self.center[1] - half, scaled_size, scaled_size)
        else:
            r = int(self.radius * self.current_scale)
        if active and not self.is_visual_only:
            glow_iter = 1 if (self.shape_type == "square" and self.number is None) else 3
            for i in range(1, glow_iter + 1):
                if self.shape_type == "square":
                    pygame.draw.rect(surface, WHITE, rect.inflate(i * 4, i * 4), 3)
                else:
                    pygame.draw.circle(surface, WHITE, self.center, r + i, 3)
        if self.image is not None:
            if self.shape_type == "square":
                img = pygame.transform.scale(self.image, (scaled_size, scaled_size))
            else:
                img = pygame.transform.scale(self.image, (2 * r, 2 * r))
            img_rect = img.get_rect(center=self.center)
            surface.blit(img, img_rect)
        else:
            if self.shape_type == "square":
                pygame.draw.rect(surface, self.color, rect)
            else:
                pygame.gfxdraw.filled_circle(surface, self.center[0], self.center[1], r, self.color)
                pygame.gfxdraw.aacircle(surface, self.center[0], self.center[1], r, self.color)
        if self.shape_type == "circle" and not self.is_lock and self.number is not None:
            font = pygame.font.Font("assets/fonts/Righteous-Regular.ttf", 20)
            text = font.render(str(self.number), True, utils.color("3C3F41"))
            text_rect = text.get_rect(center=self.center)
            surface.blit(text, text_rect)

# Class managing the level selection UI and control buttons
class LevelLoadingScreen:
    def __init__(self, screen, star_background):
        self.screen = screen
        self.background = star_background
        self.clickable_shapes = []
        self.setup_shapes()
        # Set up ESC button position and compute its rectangle once
        self.esc_pos = (10, 10)
        self.control_font = pygame.font.Font(pygame.font.match_font("arial"), 15)
        text_surf = self.control_font.render("ESC", True, (255, 255, 255))
        text_width, _ = text_surf.get_size()
        self.esc_button_rect = pygame.Rect(self.esc_pos[0], self.esc_pos[1], text_width + BTN_PADDING_X * 2, BTN_HEIGHT)
        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/menu_hover_sound.wav")
        except Exception as e:
            print("Error loading move sound:", e)
            self.move_sound = None
        try:
            self.lock_image = utils.loader_scale_image("assets/images/level_selection_screen/lock.png", 20)
        except Exception as e:
            print("Error loading lock image:", e)
            self.lock_image = None
        self.selectable_shapes = [s for s in self.clickable_shapes if s.shape_type == "circle"]
        self.selected_index = 0
        self.should_exit = False

    def draw_button(self, text, pos, extra_padding=0):
        surf = self.control_font.render(text, True, (255, 255, 255))
        text_width, _ = surf.get_size()
        width = text_width + (BTN_PADDING_X + extra_padding) * 2
        rect = pygame.Rect(pos[0], pos[1], width, BTN_HEIGHT)
        btn_surf = pygame.Surface((width, BTN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (50, 50, 50, BTN_ALPHA), btn_surf.get_rect(), border_radius=BTN_BORDER_RADIUS)
        pygame.draw.rect(btn_surf, (200, 200, 200), btn_surf.get_rect(), 2, border_radius=BTN_BORDER_RADIUS)
        self.screen.blit(btn_surf, rect.topleft)
        text_rect = surf.get_rect(center=rect.center)
        self.screen.blit(surf, text_rect)
        return rect

    def update_selection(self, new_index):
        if new_index != self.selected_index:
            self.selected_index = new_index
            if self.move_sound:
                self.move_sound.play()

    def handle_mouse_motion(self, mouse_pos):
        for i, shape in enumerate(self.selectable_shapes):
            if shape.is_hovered(mouse_pos):
                if i != self.selected_index:
                    self.update_selection(i)
                break

    def setup_shapes(self):
        total_circles_width = NUM_CIRCLES * (2 * CIRCLE_RADIUS) + (NUM_CIRCLES - 1) * CIRCLE_GAP
        row_width = total_circles_width + BOSS_OFFSET + BOSS_SIZE
        for row in range(NUM_ROWS):
            row_y = UI_TOP_MARGIN + FIRST_ROW_Y_OFFSET + row * ROW_VERTICAL_SPACING
            horizontal_offset = row * (2 * CIRCLE_RADIUS)
            start_x = (self.screen.get_width() - row_width) // 2 + horizontal_offset
            for j in range(NUM_CIRCLES):
                cx = start_x + j * (2 * CIRCLE_RADIUS + CIRCLE_GAP) + CIRCLE_RADIUS
                level_num = row * NUM_CIRCLES + j + 1
                locked = level_num > UNLOCK_THRESHOLD
                self.clickable_shapes.append(ClickableShape("circle", (cx, row_y),
                                                               radius=CIRCLE_RADIUS,
                                                               number=level_num,
                                                               is_lock=locked))
            boss_x = start_x + total_circles_width + BOSS_OFFSET + BOSS_SIZE // 2
            boss_y = row_y + BOSS_Y_SHIFT
            boss_img = utils.loader_scale_image(f"assets/images/bosses/boss_{row+1}.png", BOSS_SIZE)
            self.clickable_shapes.append(ClickableShape("square", (boss_x, boss_y),
                                                          size=BOSS_SIZE,
                                                          number=None,
                                                          is_lock=False,
                                                          image=boss_img,
                                                          is_visual_only=True))


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.esc_button_rect.collidepoint(pos):
                    self.should_exit = True
                    return "Escape"
                else:
                    for i, shape in enumerate(self.selectable_shapes):
                        if shape.is_hovered(pos):
                            self.update_selection(i)
                            # returning level back to game
                            selected = self.selectable_shapes[self.selected_index]
                            return self.summit(selected.number)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Escape"
                    # self.should_exit = True
                elif event.key == pygame.K_LEFT:
                    new_index = (self.selected_index - 1) % len(self.selectable_shapes)
                    self.update_selection(new_index)
                elif event.key == pygame.K_RIGHT:
                    new_index = (self.selected_index + 1) % len(self.selectable_shapes)
                    self.update_selection(new_index)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    selected = self.selectable_shapes[self.selected_index]
                    return self.summit(selected.number)

    def update(self, dt):
        pos = pygame.mouse.get_pos()
        for shape in self.clickable_shapes:
            active = shape.is_hovered(pos) or (shape in self.selectable_shapes and shape == self.selectable_shapes[self.selected_index])
            shape.update(dt, active)

    def draw(self):
        self.screen.fill(BLACK)
        t = pygame.time.get_ticks()
        self.background.update_and_draw(self.screen, t)
        # Draw connecting lines behind circles (solid and dotted)
        if len(self.selectable_shapes) >= 15:
            pygame.draw.line(self.screen, WHITE, self.selectable_shapes[0].center, self.selectable_shapes[4].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, WHITE, self.selectable_shapes[4].center, self.selectable_shapes[5].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, WHITE, self.selectable_shapes[5].center, self.selectable_shapes[9].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, WHITE, self.selectable_shapes[9].center, self.selectable_shapes[10].center, SOLID_LINE_THICKNESS)
            pygame.draw.line(self.screen, WHITE, self.selectable_shapes[10].center, self.selectable_shapes[14].center, SOLID_LINE_THICKNESS)
            total_circles_width = NUM_CIRCLES * (2 * CIRCLE_RADIUS) + (NUM_CIRCLES - 1) * CIRCLE_GAP
            row_width = total_circles_width + BOSS_OFFSET + BOSS_SIZE
            for row in range(NUM_ROWS):
                row_y = UI_TOP_MARGIN + FIRST_ROW_Y_OFFSET + row * ROW_VERTICAL_SPACING
                horizontal_offset = row * (2 * CIRCLE_RADIUS)
                start_x = (self.screen.get_width() - row_width) // 2 + horizontal_offset
                boss_x = start_x + total_circles_width + BOSS_OFFSET + BOSS_SIZE // 2
                boss_center = (boss_x, row_y + BOSS_Y_SHIFT)
                if row == 0:
                    draw_dotted_line(self.screen, WHITE, self.selectable_shapes[4].center, boss_center)
                elif row == 1:
                    draw_dotted_line(self.screen, WHITE, self.selectable_shapes[9].center, boss_center)
                elif row == 2:
                    draw_dotted_line(self.screen, WHITE, self.selectable_shapes[14].center, boss_center)
        pos = pygame.mouse.get_pos()
        for shape in self.clickable_shapes:
            active = shape.is_hovered(pos) or (shape in self.selectable_shapes and shape == self.selectable_shapes[self.selected_index])
            shape.draw(self.screen, active)
            if shape.shape_type == "circle" and shape.is_lock and self.lock_image is not None:
                lock_rect = self.lock_image.get_rect(center=shape.center)
                self.screen.blit(self.lock_image, lock_rect)
        # Draw ESC button without hover effect
        self.draw_button("ESC", self.esc_pos, extra_padding=0)
        # Bottom UI: "Select" label on left; two stacked buttons ("Enter" and "Space") next to it; separate left/right arrow buttons on right
        control_y = SCREEN_HEIGHT - 100
        select_text = self.control_font.render("Select", True, WHITE)
        select_rect = select_text.get_rect(midleft=(20, control_y))
        self.screen.blit(select_text, select_rect)
        buttons_x = 20 + 40
        self.draw_button("Enter", (buttons_x, control_y - 30), extra_padding=10)
        self.draw_button("Space", (buttons_x, control_y + 5), extra_padding=10)
        left_arrow_pos = (SCREEN_WIDTH - 200, control_y - 10)
        right_arrow_width = self.control_font.size("Right Arrow")[0] + BTN_PADDING_X * 2
        right_arrow_pos = (SCREEN_WIDTH - right_arrow_width - 10, control_y - 10)
        self.draw_button("Left Arrow", left_arrow_pos)
        self.draw_button("Right Arrow", right_arrow_pos)
        pygame.display.flip()

    def summit(self, number):
        return {"Level-Selected": number}


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("New Level Selection Screen")
    clock = pygame.time.Clock()
    shapes_screen = LevelLoadingScreen(screen)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        shapes_screen.handle_events(events)
        shapes_screen.update(dt)
        shapes_screen.draw()
        if shapes_screen.should_exit:
            running = False
    pygame.quit()

if __name__ == "__main__":
    main()
