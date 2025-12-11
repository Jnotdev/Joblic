import pygame
import random
import os
from animation import Animation
from particles import ParticleSystem
from collisions import detect_enemy_player_collisions
from title_screen import show_title_screen
import mouse
import mixer  # initializes audio playback (primary + secondary overlay)

# initialize pygame
pygame.init()
pygame.mixer.init()


# display
WIDTH, HEIGHT = 1400, 900

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("joblic")
# initialize custom cursor (will look for `images/cursor.png`)
try:
    mouse.init_custom_cursor()
except Exception:
    pass

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0) 
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)

BACKGROUND_COLOR = (50, 150, 200)

# game
running = True

FPS = 60
clock = pygame.time.Clock()

player_size = 50
player_x = WIDTH // 2 - player_size // 2
player_y = HEIGHT - player_size - 100
player_speed = 35  # pixels per second (used when applying to velocity)
player_xvel = 0
player_yvel = 0
player_horidir = -1 # -1 is left and 1 is right

# ANIMATION CONFIGURATION 
# Player Idle Animation Settings
PLAYER_IDLE_FRAMES = 4
PLAYER_IDLE_SPEED = 0.12  # seconds per frame

# Player Walking Animation Settings
PLAYER_WALK_FRAMES = 4
PLAYER_WALK_SPEED = 0.08  # seconds per frame


# load player animation (spritesheet - idle animation)
image_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'images', 'player.png'))
use_anim = False
player_anim = None
try:
    player_anim = Animation(image_path, frame_count=PLAYER_IDLE_FRAMES, frame_duration=PLAYER_IDLE_SPEED)
    use_anim = True
except Exception as e:
    print('Warning: failed to load player animation:', e)
    use_anim = False

# load player walking animation
image_path_walk = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'images', 'player_walk.png'))
player_walk_anim = None
try:
    player_walk_anim = Animation(image_path_walk, frame_count=PLAYER_WALK_FRAMES, frame_duration=PLAYER_WALK_SPEED)
    print(f'Loaded player walking animation from: {image_path_walk}')
except Exception as e:
    print(f'Warning: failed to load player walking animation:', e)
    player_walk_anim = None

# enemies
from enemies import Enemy, spawn_enemy_random
enemies = []
wave_number = 0
wave_interval = 3000  # milliseconds between waves
last_wave_time = pygame.time.get_ticks() - wave_interval

# load enemy animation
image_path_enemy = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'images', 'enemy.png'))
enemy_anim = None
try:
    enemy_anim = Animation(image_path_enemy, frame_count=16, frame_duration=0.06)
except Exception as e:
    print('Warning: failed to load enemy animation:', e)
    enemy_anim = None

# load background image
background_image_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'images', 'background.png'))
background_image = None
try:
    background_image = pygame.image.load(background_image_path).convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    print(f'Loaded background from: {background_image_path}')
except Exception as e:
    print(f'Warning: failed to load background image from {background_image_path}:', e)
    background_image = None

# particle system for player walking
particle_system = ParticleSystem(size_multiplier=4.0, color=(150, 150, 150))
particle_emit_timer = 0.0

# particle system for enemies (red particles)
enemy_particle_system = ParticleSystem(size_multiplier=3.0, color=(255, 100, 100))

# Control for enemy particle color - change this to adjust enemy particle appearance
ENEMY_PARTICLE_COLOR = (165, 117, 70)  

# Load custom font for HUD
hud_font = None
font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'fonts', 'font.ttf'))
try:
    hud_font = pygame.font.Font(font_path, 32)
    print(f'Loaded custom font from: {font_path}')
except Exception as e:
    print(f'Warning: failed to load custom font from {font_path}:', e)
    hud_font = pygame.font.SysFont(None, 32)  # fallback to system font

# ============ SCREEN SHAKE CONFIGURATION ============
SCREEN_SHAKE_ENABLED = True
SCREEN_SHAKE_INTENSITY = 6  # pixels (change this to adjust shake strength)
SCREEN_SHAKE_DURATION = 0.18  # seconds (how long the shake lasts)
# ====================================================

# Screen shake variables
screen_shake_timer = 0.0
screen_shake_offset_x = 0
screen_shake_offset_y = 0

# set keys not released unready
waiting_for_release = False

# Create a temporary surface for rendering (used for screen shake effect)
temp_surface = pygame.Surface((WIDTH, HEIGHT))

# Show title screen before starting the game
if not show_title_screen(screen, WIDTH, HEIGHT):
    pygame.quit()
    exit()

while running:
    # frame timing
    dt = clock.tick(FPS) / 1000.0

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    

    # player movement (velocity based)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_x > 0:
        player_xvel += -player_speed * dt
        player_horidir = -1
    if keys[pygame.K_d] and player_x < WIDTH - player_size:
        player_xvel += player_speed * dt
        player_horidir = 1
    if keys[pygame.K_w] and player_y > 0:
        player_yvel += -player_speed * dt
    if keys[pygame.K_s] and player_y < HEIGHT - player_size:
        player_yvel += player_speed * dt
    


    # player dash (based on horizontal direction)
    if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                if not waiting_for_release:
                    print("Shift pressed. Now waiting for release...")
                    waiting_for_release = True
                    dash_speed = 20  # pixels per second
                    player_xvel += dash_speed * player_horidir
                    
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
            waiting_for_release = False


    # simple damping
    player_xvel = player_xvel / (1 + 6 * dt)
    player_yvel = player_yvel / (1 + 6 * dt)
    player_x += player_xvel
    player_y += player_yvel

    # keep player on screen
    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(200, min(HEIGHT - player_size, player_y))

    # emit walking particles when moving
    moving_threshold = 1.0
    is_moving = abs(player_xvel) > moving_threshold or abs(player_yvel) > moving_threshold
    if is_moving:
        particle_emit_timer += dt
        if particle_emit_timer >= 0.05:  # emit every 0.05 seconds while moving
            particle_emit_timer = 0.0
            # emit particles from player's feet
            particle_system.emit(
                player_x + player_size // 2,
                player_y + player_size,
                count=3,
                color=(224, 184, 146),
                speed_range=(30, 80),
                size_range=(2, 5),
            )
    else:
        particle_emit_timer = 0.0

    # update particles
    particle_system.update(dt)
    enemy_particle_system.update(dt)

    # spawn waves
    now = pygame.time.get_ticks()
    if now - last_wave_time >= wave_interval:
        wave_number += 1
        # increase enemies per wave gradually
        spawn_count = 3 + wave_number  # simple ramp
        for i in range(spawn_count):
            # create a copy of the animation for each enemy
            enemy_anim_copy = enemy_anim.copy() if enemy_anim else None
            e = spawn_enemy_random(WIDTH, size_range=(30, 48), speed_range=(80 + wave_number * 10, 140 + wave_number * 15), animation=enemy_anim_copy, particle_system=enemy_particle_system, particle_color=ENEMY_PARTICLE_COLOR)
            enemies.append(e)
        last_wave_time = now

    # update enemies and remove offscreen ones
    for e in enemies[:]:
        e.update(dt)
        if e.is_offscreen(HEIGHT):
            enemies.remove(e)

    # check collisions between enemies and player
    player_rect = pygame.Rect(int(player_x), int(player_y), player_size, player_size)

    # define a small callback to trigger screen shake from within collisions
    def _trigger_shake(duration):
        # set the module-level screen_shake_timer
        globals()["screen_shake_timer"] = duration

    # user collision handler placeholder - add your custom actions here
    def on_enemy_collision(enemy):
        # TODO: add your custom collision handling here (e.g., reduce health, knockback)
        # Example:
        # player_health -= 1
        pass

    # detect collisions; this will call _trigger_shake before on_enemy_collision
    collided_enemies = detect_enemy_player_collisions(player_rect, enemies, on_collision=on_enemy_collision, shake_callback=_trigger_shake, shake_duration=0.12)

    # update screen shake
    if screen_shake_timer > 0:
        screen_shake_timer -= dt
        if screen_shake_timer <= 0:
            screen_shake_offset_x = 0
            screen_shake_offset_y = 0
        else:
            screen_shake_offset_x = random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)
            screen_shake_offset_y = random.randint(-SCREEN_SHAKE_INTENSITY, SCREEN_SHAKE_INTENSITY)

    # draw everything onto temporary surface
    if background_image:
        temp_surface.blit(background_image, (0, 0))
    else:
        temp_surface.fill(BACKGROUND_COLOR)

    # draw particles
    particle_system.draw(temp_surface)
    enemy_particle_system.draw(temp_surface)

    # draw enemies
    for e in enemies:
        e.draw(temp_surface)

    # draw player (animated if available) - on top layer
    moving_threshold = 1.0
    is_moving = abs(player_xvel) > moving_threshold or abs(player_yvel) > moving_threshold

    if is_moving and player_walk_anim:
        # play walking animation when moving
        player_walk_anim.update(dt)
        player_walk_anim.draw(temp_surface, player_x, player_y, width=player_size, height=player_size)
    elif use_anim and player_anim:
        # play idle animation when not moving
        player_anim.update(dt)
        player_anim.draw(temp_surface, player_x, player_y, width=player_size, height=player_size)
    else:
        pygame.draw.rect(temp_surface, GREEN, (int(player_x), int(player_y), player_size, player_size))

    # HUD: wave display at bottom middle
    text = hud_font.render(f"Wave {wave_number}", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 60))
    temp_surface.blit(text, text_rect)

    # Blit the temp surface to the real screen with shake offset
    screen.fill(BLACK)
    screen.blit(temp_surface, (screen_shake_offset_x, screen_shake_offset_y))
    # draw custom cursor on top
    try:
        mouse.draw_cursor(screen)
    except Exception:
        pass
    pygame.display.update()


pygame.quit()