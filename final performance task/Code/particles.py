import pygame
import random
import math


class Particle:
    def __init__(self, x, y, vx=0, vy=0, size=5, color=(255, 255, 255), lifespan=0.5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.lifespan = lifespan  # seconds
        self.age = 0.0  # seconds

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # simple gravity
        self.vy += 150 * dt

    def draw(self, surface):
        if self.is_alive():
            alpha = max(0, 255 * (1 - self.age / self.lifespan))
            color = (*self.color[:3], int(alpha))
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (self.size // 2, self.size // 2), self.size // 2)
            surface.blit(s, (int(self.x) - self.size // 2, int(self.y) - self.size // 2))

    def is_alive(self):
        return self.age < self.lifespan


class ParticleSystem:
    def __init__(self, size_multiplier=1.0, color=(200, 200, 200)):
        self.particles = []
        self.size_multiplier = size_multiplier  # easy way to scale all particles
        self.color = color  # default particle color

    def emit(self, x, y, count=5, color=None, speed_range=(40, 120), size_range=(3, 8)):
        """Emit particles at position (x, y) in random directions."""
        # use system default color if not specified
        if color is None:
            color = self.color
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(speed_range[0], speed_range[1])
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 60  # slight upward bias
            size = int(random.randint(size_range[0], size_range[1]) * self.size_multiplier)
            p = Particle(x, y, vx=vx, vy=vy, size=size, color=color, lifespan=random.uniform(0.3, 0.6))
            self.particles.append(p)

    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.is_alive():
                self.particles.remove(p)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)