import pygame
import math
import random

# Screen and effect parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
RING_RADIUS = 150        # Radius where particles spawn
RING_WIDTH = 1           # 1-pixel wide ring outline
PARTICLE_COUNT = 300     # Total number of particles
CENTER_THRESHOLD = 10    # When particle is within this distance of center, re-spawn it

# Speed range for particles (they move at random speeds)
MIN_SPEED = 1.0
MAX_SPEED = 3.0

class Particle:
    def __init__(self, center, ring_radius):
        self.center = center
        self.ring_radius = ring_radius
        self.spawn()

    def spawn(self):
        # Spawn the particle at a random angle along the ring's edge.
        self.angle = random.uniform(0, 2 * math.pi)
        self.x = self.center[0] + self.ring_radius * math.cos(self.angle)
        self.y = self.center[1] + self.ring_radius * math.sin(self.angle)
        # Assign a random speed
        self.speed = random.uniform(MIN_SPEED, MAX_SPEED)

    def update(self):
        # Compute the ideal angle from the current position toward the center.
        dx = self.center[0] - self.x
        dy = self.center[1] - self.y
        ideal_angle = math.atan2(dy, dx)
        # Add a small random deviation (in radians) to vary the paths.
        new_angle = ideal_angle + random.uniform(-0.05, 0.05)
        # Update the particle's position based on the new angle and its speed.
        self.x += math.cos(new_angle) * self.speed
        self.y += math.sin(new_angle) * self.speed

    def draw(self, screen):
        # Draw the particle as a 1-pixel white dot.
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 1)

    def check_reset(self):
        # If the particle is close to the center, respawn it at the ring edge.
        dx = self.center[0] - self.x
        dy = self.center[1] - self.y
        if math.hypot(dx, dy) < CENTER_THRESHOLD:
            self.spawn()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sci-Fi Ring Particle Effect")
    clock = pygame.time.Clock()
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Create particles that spawn along the ring's edge.
    particles = [Particle(center, RING_RADIUS) for _ in range(PARTICLE_COUNT)]

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update each particle and check if it needs to respawn.
        for p in particles:
            p.update()
            p.check_reset()

        screen.fill((0, 0, 0))
        # Draw the ring outline.
        pygame.draw.circle(screen, (100, 100, 100), center, RING_RADIUS, RING_WIDTH)
        # Draw each particle.
        for p in particles:
            p.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
