import pygame
import math
import random

# Screen and effect parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
RING_RADIUS = 150
RING_WIDTH = 1         # 1 pixel wide ring
PARTICLE_SPEED = 2     # How fast particles move toward the center
PARTICLE_COUNT = 300   # Number of particles
CENTER_THRESHOLD = 10  # Distance from center to re-spawn particle

class Particle:
    def __init__(self, center, ring_radius):
        self.center = center
        # Spawn at a random angle along the ring's edge
        self.angle = random.uniform(0, 2 * math.pi)
        self.x = center[0] + ring_radius * math.cos(self.angle)
        self.y = center[1] + ring_radius * math.sin(self.angle)
        # Compute a normalized vector from current position toward the center
        dx = center[0] - self.x
        dy = center[1] - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            self.vx = (dx / distance) * PARTICLE_SPEED
            self.vy = (dy / distance) * PARTICLE_SPEED
        else:
            self.vx = self.vy = 0
        self.color = (255, 255, 255)  # White particles
        self.radius = 2             # Particle drawn as a small circle

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def reset(self, ring_radius):
        # Respawn the particle at a new random angle along the ring
        self.angle = random.uniform(0, 2 * math.pi)
        self.x = self.center[0] + ring_radius * math.cos(self.angle)
        self.y = self.center[1] + ring_radius * math.sin(self.angle)
        dx = self.center[0] - self.x
        dy = self.center[1] - self.y
        distance = math.hypot(dx, dy)
        if distance != 0:
            self.vx = (dx / distance) * PARTICLE_SPEED
            self.vy = (dy / distance) * PARTICLE_SPEED

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sci-Fi Ring Effect")
    clock = pygame.time.Clock()
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Create a list of particles spawning at the ring edge.
    particles = [Particle(center, RING_RADIUS) for _ in range(PARTICLE_COUNT)]

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update each particle's position.
        for p in particles:
            p.update()
            # If particle is close enough to the center, reset it to the ring edge.
            dx = p.x - center[0]
            dy = p.y - center[1]
            if math.hypot(dx, dy) < CENTER_THRESHOLD:
                p.reset(RING_RADIUS)

        screen.fill((0, 0, 0))
        # Draw the ring outline (sci-fi style).
        pygame.draw.circle(screen, (100, 100, 100), center, RING_RADIUS, RING_WIDTH)
        # Draw each particle.
        for p in particles:
            p.draw(screen)

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
