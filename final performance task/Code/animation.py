import pygame


class Animation:
    """Simple sprite-sheet animation helper.

    Assumptions:
    - The sprite sheet contains frames laid out horizontally in a single row.
    - `frame_count` specifies how many frames are in the sheet.
    """

    def __init__(self, image_path, frame_count=4, frame_duration=0.12):
        self.sheet = pygame.image.load(image_path).convert_alpha()
        self.frame_count = frame_count
        self.frame_duration = frame_duration  # seconds per frame

        sheet_w, sheet_h = self.sheet.get_size()
        self.frame_width = sheet_w // frame_count
        self.frame_height = sheet_h

        # prepare frames
        self.frames = []
        for i in range(frame_count):
            rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame = self.sheet.subsurface(rect).copy()
            self.frames.append(frame)

        self.current = 0
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer -= self.frame_duration
            self.current = (self.current + 1) % self.frame_count

    def get_frame(self):
        return self.frames[self.current]

    def set_frame(self, index: int):
        """Set the current frame index and reset the frame timer."""
        self.current = int(index) % self.frame_count
        self.timer = 0.0

    def copy(self):
        """Create an independent copy of this animation with reset state."""
        new_anim = Animation.__new__(Animation)
        new_anim.sheet = self.sheet
        new_anim.frame_count = self.frame_count
        new_anim.frame_duration = self.frame_duration
        new_anim.frame_width = self.frame_width
        new_anim.frame_height = self.frame_height
        new_anim.frames = self.frames.copy()
        new_anim.current = 0
        new_anim.timer = 0.0
        return new_anim

    def draw(self, surface, x, y, width=None, height=None):
        frame = self.get_frame()
        if width is not None and height is not None:
            frame = pygame.transform.scale(frame, (int(width), int(height)))
        surface.blit(frame, (int(x), int(y)))
