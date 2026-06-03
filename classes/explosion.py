class Explosion:
    def __init__(self, x, y, frames, ticks_per_frame=3):
        self.x = x
        self.y = y
        self.frames = frames
        self.frame_index = 0
        self.tick = 0
        self.ticks_per_frame = ticks_per_frame
        self.alive = True

    def update(self):
        self.tick += 1
        if self.tick % self.ticks_per_frame == 0:
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.alive = False
                

    def draw(self, surf, cam_x=0, cam_y=0):
        if not self.alive or self.frame_index >= len(self.frames):
            return
        frame = self.frames[self.frame_index]
        surf.blit(frame, (
            int(self.x - cam_x - frame.get_width()  / 2),
            int(self.y - cam_y - frame.get_height() / 2),
        ))
