import random


class Enemy:
    def __init__(self, x, y, size=80, speed=120, color=(224, 184, 146), animation=None, particle_system=None, particle_color=None):
        # position
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed  # pixels per second
        self.color = color
        self.animation = animation  # optional Animation instance
        self.particle_system = particle_system  # optional ParticleSystem for effects
        self.particle_color = particle_color  # color for particles emitted by this enemy
        self.particle_emit_timer = 0.0

    def update(self, dt):
        # move downward
        self.y += self.speed * dt
        # update animation if available
        if self.animation:
            self.animation.update(dt)
        
        # emit particles while moving (similar to player footsteps)
        if self.particle_system:
            self.particle_emit_timer += dt
            if self.particle_emit_timer >= 0.08:  # emit every 0.08 seconds
                self.particle_emit_timer = 0.0
                self.particle_system.emit(
                    self.x + self.size // 2,
                    self.y + self.size,
                    count=2,
                    color=self.particle_color,  # use this enemy's particle color
                    speed_range=(20, 60),
                    size_range=(2, 4)
                )

    def draw(self, surface):
        import pygame

        if self.animation:
            self.animation.draw(surface, int(self.x), int(self.y), width=self.size, height=self.size)
        else:
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), self.size, self.size))

    def is_offscreen(self, screen_height):
        return self.y > screen_height


def spawn_enemy_random(screen_width, size_range=(30, 50), speed_range=(80, 180), animation=None, particle_system=None, particle_color=None):
    size = random.randint(size_range[0], size_range[1])
    x = random.randint(0, max(0, screen_width - size))
    y = -size
    speed = random.uniform(speed_range[0], speed_range[1])
    return Enemy(x, y, size=size, speed=speed, animation=animation, particle_system=particle_system, particle_color=particle_color)
