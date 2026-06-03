import math
import pygame

class Torpedo:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle  # degrees
        self.speed = 0.5
        self.alive = True
        self.damage = 60
        self.trail = []
        self.max_trail = 35

    def update(self, screen_width, screen_height):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        rad = math.radians(self.angle)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed

        if not (-4000 <= self.x <= 4800 and -4000 <= self.y <= 4600):
            self.alive = False

    def draw(self, screen, cam_x=0, cam_y=0):
        for i, (tx, ty) in enumerate(self.trail):
            t = i / max(1, len(self.trail) - 1)
            r = int(0  + 180 * t)
            g = int(33 + 167 * t)
            b = int(48 + 172 * t)
            size = max(1, int(3 * t))
            pygame.draw.circle(screen, (r, g, b), (int(tx - cam_x), int(ty - cam_y)), size)

        if not self.alive:
            return

        sx, sy = self.x - cam_x, self.y - cam_y
        rad = math.radians(self.angle)
        fx, fy = math.sin(rad), -math.cos(rad)
        rx, ry = math.cos(rad),  math.sin(rad)
        half_l, half_w = 5, 1
        corners = [
            (sx + fx*half_l + rx*half_w, sy + fy*half_l + ry*half_w),
            (sx + fx*half_l - rx*half_w, sy + fy*half_l - ry*half_w),
            (sx - fx*half_l - rx*half_w, sy - fy*half_l - ry*half_w),
            (sx - fx*half_l + rx*half_w, sy - fy*half_l + ry*half_w),
        ]
        pygame.draw.polygon(screen, (0, 0, 0), corners)

    def hits(self, ship):
        return math.hypot(self.x - ship.x, self.y - ship.y) < 20
