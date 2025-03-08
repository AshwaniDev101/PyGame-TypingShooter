import pygame

from config import utils

from config import constants
from enemies.enemy import Enemy


class CheckpointDivider(Enemy):
    def __init__(self, player, checkpoint_manager, checkpoint_id:int):
        super().__init__(player)

        self.id = checkpoint_id
        self.checkpoint_manager = checkpoint_manager
        self.player = player

        self.y = -50  # Initial Y position
        self.checkpoint_text = f"Checkpoint"
        self.color = utils.color("ffffff")
        self.speed = 2  # Speed at which the line moves down
        self.triggered = False

    def move(self, game_over):
        self.y += self.speed  # Move down
        self.check_collision()

    def draw(self, screen):
        self.draw_dashed_line(screen,(0, self.y), (constants.SCREEN_WIDTH, self.y))

    def draw_dashed_line(self, screen, start_pos, end_pos, dash_length=10):
        font = pygame.font.Font(None, 30)
        text_surface = font.render(self.checkpoint_text, True, self.color)
        font = pygame.font.Font(None, 40)
        text_number = font.render(f"{self.id}", True, utils.color("FF9DE8"))
        screen.blit(text_surface, (end_pos[0] - text_surface.get_width()- 40, start_pos[1] - 30))  # Text slightly offset
        screen.blit(text_number, (end_pos[0] - 30, start_pos[1] - 36))  # Text slightly offset

        x1, y1 = start_pos
        x2, y2 = end_pos
        dx, dy = x2 - x1, y2 - y1
        distance = (dx ** 2 + dy ** 2) ** 0.5
        dashes = int(distance // dash_length)
        dash_x, dash_y = dx / dashes, dy / dashes

        for i in range(0, dashes, 2):
            start = (x1 + i * dash_x, y1 + i * dash_y)
            end = (x1 + (i + 1) * dash_x, y1 + (i + 1) * dash_y)
            pygame.draw.line(screen, self.color, start, end, 2)

    def check_collision(self):
        # Create a thin rectangle along the dashed line

        if self.y >= self.player.rect.top  and not self.triggered:
            self.trigger_checkpoint()
            self.triggered = True

    def trigger_checkpoint(self):
        # Replace this with your actual checkpoint trigger logic
        self.checkpoint_manager.save_checkpoint(self.id, self.player)