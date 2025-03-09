import random
import pygame
import math
from config import constants, utils
from enemies.enemy import Enemy

class EnemyProximityMines(Enemy):
    """
    An enemy that moves toward the player when close enough and displays a glowing,
    pulsating effect along with a dotted line indicator.
    """
    def __init__(self, player):
        """
        Initialize the enemy with a random horizontal start position (off-screen vertically)
        and set up its movement and visual effect attributes.
        """
        super().__init__(player)
        # Set initial position: random X between 50 and screen width-50, off-screen Y (-50)
        self.rect = pygame.Rect(
            random.randint(50, constants.SCREEN_WIDTH - 50),
            -50,
            20, 20  # Enemy size is small
        )
        # self.word = "badname"  # Label or identifier for the enemy

        # Movement attributes
        self.angle = 0
        self.speed = 2
        self.entry_done = True  # Starts moving immediately
        self.bomb_activation_distance = 300  # Distance threshold to start homing toward the player

        # Glowing (pulsating) effect variables
        self.pulse = 0           # Controls the pulsating effect magnitude
        self.pulse_direction = 1 # Determines if the pulse is increasing or decreasing

    def _get_vector_to_player(self):
        """
        Calculate the vector from this enemy to the player along with its distance.
        Returns:
            dx (float): Difference in X coordinates.
            dy (float): Difference in Y coordinates.
            distance (float): Euclidean distance between enemy and player.
            ndx (float): Normalized x-direction (dx / distance).
            ndy (float): Normalized y-direction (dy / distance).
        """
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:
            ndx = dx / distance
            ndy = dy / distance
        else:
            ndx, ndy = 0, 0
        return dx, dy, distance, ndx, ndy

    def move(self, game_over):
        """
        Update the enemy's position. If the game is over, move straight down.
        Otherwise, if the enemy is within bomb activation distance, move toward the player;
        if not, move straight down. Also update the pulsating effect and apply any pushback.
        """
        if game_over:
            # When game over, move downwards faster.
            self.rect.y += self.speed * 2
            return

        # Get vector information to the player.
        _, _, distance, ndx, ndy = self._get_vector_to_player()

        if distance > self.bomb_activation_distance:
            # If far from the player, move straight down.
            self.rect.y += self.speed
        else:
            # Move toward the player.
            self.rect.x += ndx * self.speed
            self.rect.y += ndy * self.speed
            # Rotate enemy to face the player.
            self.angle = math.degrees(math.atan2(-ndy, ndx)) + 90

        # Update the pulsating effect.
        self._update_pulse()
        # Apply pushback space_elements (inherited or custom logic).
        self.move_handle_pushback()

    def _update_pulse(self):
        """
        Update the pulse value to create a pulsating effect.
        The pulse oscillates between -2 and 2.
        """
        self.pulse += self.pulse_direction * 0.2  # Subtle change for a smooth effect
        if self.pulse > 2 or self.pulse < -2:
            self.pulse_direction *= -1  # Reverse the pulse direction at bounds

    def draw(self, screen):
        """
        Render the enemy on the screen by drawing its glowing effect,
        dotted line (if within activation distance), and word label.
        """
        self._draw_glowing_effect(screen)
        self._draw_dotted_line_if_close(screen)
        # draw_word is assumed to be defined in the parent class or elsewhere.
        self.draw_word(screen)

    def _draw_glowing_effect(self, screen):
        """
        Draw the enemy's glowing effect which consists of an inner core and outer aura circles.
        """
        # Core size changes with pulse to create a pulsating effect.
        core_size = 10 + self.pulse
        # Draw the inner core circle (main glow).
        pygame.draw.circle(screen, utils.color("FF3E31"), self.rect.center, core_size)
        # Draw an outer aura circle with a thin white border.
        pygame.draw.circle(screen, utils.color("ffffff"), self.rect.center, core_size + 10, 1)
        # Optionally, draw an extended aura to indicate bomb activation range.
        pygame.draw.circle(screen, utils.color("ffffff"), self.rect.center, self.bomb_activation_distance-(self.player.rect.width / 2), 1)

    def _draw_dotted_line_if_close(self, screen):
        """
        If the enemy is within the bomb activation distance from the player,
        draw a dotted line from the enemy to the player.
        """
        # Calculate the distance to the player.
        _, _, distance, _, _ = self._get_vector_to_player()
        if distance < self.bomb_activation_distance:
            self._draw_dotted_line(screen)

    def _draw_dotted_line(self, screen):
        """
        Draw a dotted line from the enemy's center to the player's center.
        The line is made up of short segments with gaps between them.
        """
        start_pos = self.rect.center
        end_pos = self.player.rect.center
        color = (255, 255, 255)  # White color for the dotted line
        segment_length = 2       # Length of each dot segment
        gap_length = 5           # Gap between segments

        # Calculate the normalized direction vector.
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            return  # Prevent division by zero
        dx /= distance
        dy /= distance

        # Determine the number of segments to draw.
        num_segments = int(distance // (segment_length + gap_length))
        for i in range(num_segments):
            # Calculate start and end positions for each segment.
            seg_start_x = int(start_pos[0] + i * (dx * (segment_length + gap_length)))
            seg_start_y = int(start_pos[1] + i * (dy * (segment_length + gap_length)))
            seg_end_x = int(seg_start_x + dx * segment_length)
            seg_end_y = int(seg_start_y + dy * segment_length)
            # Draw the segment.
            pygame.draw.line(screen, color, (seg_start_x, seg_start_y), (seg_end_x, seg_end_y), 2)
