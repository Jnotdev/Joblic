import pygame
import os

_cursor_img = None
_cursor_hotspot = (0, 0)
_cursor_scale = 2.0
_visible = True


def init_custom_cursor(image_path=None, hotspot=None, scale=2.0):
    """Load a custom cursor image and hide the system cursor.

    - image_path: path to the cursor image. If None, will look for '../images/cursor.png'.
    - hotspot: (x,y) pixel inside the image to align with the pointer position.
    - scale: float scale to apply when drawing the cursor.
    """
    global _cursor_img, _cursor_hotspot, _cursor_scale, _visible
    if image_path is None:
        base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
        image_path = os.path.join(base, 'images', 'cursor.png')

    try:
        img = pygame.image.load(image_path)
        # keep alpha if present, otherwise convert and set white -> transparent
        if img.get_alpha() is not None:
            _cursor_img = img.convert_alpha()
        else:
            _cursor_img = img.convert()
            _cursor_img.set_colorkey((255, 255, 255))
        # default hotspot: center of image when not provided
        if hotspot is None:
            w, h = _cursor_img.get_size()
            _cursor_hotspot = (w // 2, h // 2)
        else:
            _cursor_hotspot = hotspot
        _cursor_scale = float(scale)
        pygame.mouse.set_visible(False)
        _visible = True
    except Exception:
        # If we fail to load, leave system cursor visible
        _cursor_img = None
        pygame.mouse.set_visible(True)
        _visible = False


def draw_cursor(surface):
    """Draw the custom cursor (if loaded) onto `surface` at current mouse position.
    If no custom cursor is loaded, does nothing.
    """
    global _cursor_img
    if not _cursor_img:
        return
    try:
        mx, my = pygame.mouse.get_pos()
        img = _cursor_img
        if _cursor_scale != 1.0:
            # scale image on the fly
            w, h = img.get_size()
            img = pygame.transform.scale(img, (max(1, int(w * _cursor_scale)), max(1, int(h * _cursor_scale))))
        hotx, hoty = _cursor_hotspot
        # adjust by scale
        hotx = int(hotx * _cursor_scale)
        hoty = int(hoty * _cursor_scale)
        surface.blit(img, (mx - hotx, my - hoty))
    except Exception:
        # fail quietly
        pass


def hide_system_cursor():
    pygame.mouse.set_visible(False)


def show_system_cursor():
    pygame.mouse.set_visible(True)
