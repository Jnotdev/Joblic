import pygame


def detect_enemy_player_collisions(player_rect, enemies, on_collision=None, shake_callback=None, shake_duration=0.12):
    """Check collisions between a player rect and a list of Enemy instances.

    - player_rect: pygame.Rect for the player
    - enemies: iterable of objects with x, y, size attributes
    - on_collision: optional callback called with the enemy instance when collision occurs
    - shake_callback: optional callback called with a duration (seconds) to trigger a screen shake
    - shake_duration: default duration passed to shake_callback when a collision happens

    Returns a list of enemies that collided (caller may remove or handle them).
    """
    collided = []
    for e in enemies:
        enemy_rect = pygame.Rect(int(e.x), int(e.y), e.size, e.size)
        if player_rect.colliderect(enemy_rect):
            collided.append(e)
            # trigger shake first (if available)
            if shake_callback:
                try:
                    shake_callback(shake_duration)
                except Exception:
                    pass
            # then call user-provided collision handler
            if on_collision:
                try:
                    on_collision(e)
                except Exception:
                    pass
    return collided
