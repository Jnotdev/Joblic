import pygame
import os
import time
import mouse
import math


def _load_image(path):
    try:
        return pygame.image.load(path)
    except Exception:
        return None


def _fit_image(img, max_w, max_h, allow_upscale=True):
    iw, ih = img.get_size()
    if not allow_upscale:
        scale = min(1.0, min(max_w / iw, max_h / ih))
    else:
        scale = min(max_w / iw, max_h / ih)
    new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
    if new_size != (iw, ih):
        return pygame.transform.scale(img, new_size)
    return img


def show_title_screen(screen, WIDTH, HEIGHT):
    """Render an image-only title screen using the provided `screen` surface.

    Returns True to start the game, False to quit.
    """
    # Do not re-init display here; expect `screen` provided from `game.py`.
    if screen is None:
        screen = pygame.display.get_surface()
        if screen is None:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    FPS = 60

    # Appearance settings (larger sizes per request)
    TITLE_MAX_W, TITLE_MAX_H = 900, 260
    BUTTON_MAX_W, BUTTON_MAX_H = 420, 140
    title_y = int(HEIGHT * 0.25)
    button_center_y = int(HEIGHT * 0.62)

    # Load images (background, title, button, hover)
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
    bg_path = os.path.join(base, 'images', 'background.png')
    title_path = os.path.join(base, 'images', 'title.png')
    btn_path = os.path.join(base, 'images', 'button.png')
    btn_hover_path = os.path.join(base, 'images', 'button_hover.png')

    background = _load_image(bg_path)
    if background:
        try:
            background = background.convert()
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        except Exception:
            background = None

    raw_title = _load_image(title_path)
    title_img = None
    if raw_title:
        # prefer alpha; if not present, set white colorkey to remove white background
        if raw_title.get_alpha() is not None:
            title_img = raw_title.convert_alpha()
        else:
            title_img = raw_title.convert()
            title_img.set_colorkey((255, 255, 255))
        title_img = _fit_image(title_img, TITLE_MAX_W, TITLE_MAX_H, allow_upscale=True)

    raw_btn = _load_image(btn_path)
    btn_img = None
    if raw_btn:
        if raw_btn.get_alpha() is not None:
            btn_img = raw_btn.convert_alpha()
        else:
            btn_img = raw_btn.convert()
            btn_img.set_colorkey((255, 255, 255))
        btn_img = _fit_image(btn_img, BUTTON_MAX_W, BUTTON_MAX_H, allow_upscale=True)

    raw_btn_hover = _load_image(btn_hover_path)
    btn_hover_img = None
    if raw_btn_hover:
        if raw_btn_hover.get_alpha() is not None:
            btn_hover_img = raw_btn_hover.convert_alpha()
        else:
            btn_hover_img = raw_btn_hover.convert()
            btn_hover_img.set_colorkey((255, 255, 255))
        # match hover to btn_img size if available
        if btn_img:
            btn_hover_img = pygame.transform.scale(btn_hover_img, btn_img.get_size())
        else:
            btn_hover_img = _fit_image(btn_hover_img, BUTTON_MAX_W, BUTTON_MAX_H, allow_upscale=True)

    # Button rect: if we have an image use that size, otherwise use default max
    if btn_img:
        bw, bh = btn_img.get_size()
    else:
        bw, bh = BUTTON_MAX_W, BUTTON_MAX_H
    button_rect = pygame.Rect(0, 0, bw, bh)
    button_rect.center = (WIDTH // 2, button_center_y)

    # Dynamic sizing variables
    default_btn_w, default_btn_h = bw, bh
    target_btn_w, target_btn_h = bw, bh
    current_btn_w, current_btn_h = float(bw), float(bh)
    HOVER_INCREMENT = 50
    HOVER_SCALE = 1.06

    # Load click sound (optional)
    click_sound = None
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        click_path = os.path.join(base, 'sound', 'click.wav')
        if os.path.exists(click_path):
            click_sound = pygame.mixer.Sound(click_path)
    except Exception:
        click_sound = None
    # initialize custom cursor (optional)
    try:
        mouse.init_custom_cursor()
    except Exception:
        pass

    # Fade-in variables
    fade_alpha = 0
    fade_speed = 10  # larger = faster

    # Animation timer for floating/rotation
    anim_t = 0.0
    FLOAT_AMPLITUDE = 18      # pixels
    FLOAT_FREQUENCY = 0.6     # Hz
    ROTATION_AMPLITUDE = 6.0  # degrees
    ROTATION_FREQUENCY = 0.9  # Hz

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        anim_t += dt

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1 and button_rect.collidepoint(ev.pos):
                    if click_sound:
                        try:
                            click_sound.play()
                        except Exception:
                            pass
                    # small delay so click sound can start
                    pygame.display.flip()
                    time.sleep(0.15)
                    return True
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if click_sound:
                        try:
                            click_sound.play()
                        except Exception:
                            pass
                    pygame.display.flip()
                    time.sleep(0.15)
                    return True

        mx, my = pygame.mouse.get_pos()

        # determine hover and set target size accordingly (default or default + 50)
        hover = button_rect.collidepoint((mx, my))
        if hover:
            target_btn_w = default_btn_w + HOVER_INCREMENT
            target_btn_h = default_btn_h + HOVER_INCREMENT
        else:
            target_btn_w = default_btn_w
            target_btn_h = default_btn_h

        # update dynamic button size toward the target using easing: ((target) - current) / 15
        current_btn_w += (target_btn_w - current_btn_w) / 15.0
        current_btn_h += (target_btn_h - current_btn_h) / 15.0
        # ensure minimum size
        cur_w = max(4, int(current_btn_w))
        cur_h = max(4, int(current_btn_h))

        # update button_rect to match current size and keep center
        button_rect.width, button_rect.height = cur_w, cur_h
        button_rect.center = (WIDTH // 2, button_center_y)

        # draw background
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((50, 150, 200))

        # dark overlay to help images read
        overlay = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 90))
        screen.blit(overlay, (0, 0))

        # draw title with floating + rotation animation
        if title_img:
            # compute offsets
            y_offset = math.sin(anim_t * 2 * math.pi * FLOAT_FREQUENCY) * FLOAT_AMPLITUDE
            angle = math.sin(anim_t * 2 * math.pi * ROTATION_FREQUENCY) * ROTATION_AMPLITUDE
            # rotate (and keep smooth scaling)
            rotated_title = pygame.transform.rotozoom(title_img, angle, 1.0)
            tr = rotated_title.get_rect(center=(WIDTH // 2, title_y + int(y_offset)))
            screen.blit(rotated_title, tr)

        # draw button with slight hover scale
        if btn_img or btn_hover_img:
            # compute draw size (apply hover scale if no hover image)
            if hover and not btn_hover_img:
                draw_w = max(4, int(cur_w * HOVER_SCALE))
                draw_h = max(4, int(cur_h * HOVER_SCALE))
            else:
                draw_w, draw_h = cur_w, cur_h

            if hover and btn_hover_img:
                scaled = pygame.transform.smoothscale(btn_hover_img, (draw_w, draw_h))
                br = scaled.get_rect(center=button_rect.center)
                screen.blit(scaled, br)
            elif btn_img:
                scaled = pygame.transform.smoothscale(btn_img, (draw_w, draw_h))
                br = scaled.get_rect(center=button_rect.center)
                screen.blit(scaled, br)
        else:
            # placeholder rounded rect
            color = (170, 210, 255) if hover else (120, 190, 255)
            pygame.draw.rect(screen, color, button_rect, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, width=3, border_radius=12)

        # simple fade-in
        if fade_alpha < 255:
            fade_alpha = min(255, fade_alpha + fade_speed)
            fade_surf = pygame.Surface((WIDTH, HEIGHT))
            fade_surf.set_alpha(255 - fade_alpha)
            fade_surf.fill((0, 0, 0))
            screen.blit(fade_surf, (0, 0))

        # draw custom cursor on top
        try:
            mouse.draw_cursor(screen)
        except Exception:
            pass

        pygame.display.flip()

    return True
