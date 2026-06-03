import math
import pygame
import random
from classes.explosion import Explosion

class Projectile:
    def __init__(self, x, y, z, launch_angle, angle, speed=30, damage=random.randint(10, 20), color=(160, 160, 160), half_l=4, half_w=1):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle
        self.speed = speed
        self.alive = True
        self.damage = damage
        self.color = color
        self.half_l = half_l
        self.half_w = half_w
        self.launch_angle = launch_angle
        self.vz = speed * math.sin(launch_angle)
        self.gravity = 0.1
        self.splash_frames = None
        self.splash = None

    def update(self, screen_width, screen_height):
        if self.splash:
            self.splash.update()
            if not self.splash.alive:
                self.alive = False
            return

        rad = math.radians(self.angle)
        horizontal_speed = self.speed * math.cos(self.launch_angle)

        self.x += math.sin(rad) * horizontal_speed
        self.y -= math.cos(rad) * horizontal_speed
        self.z += self.vz
        self.vz -= self.gravity

        if self.z <= 0 and self.vz < 0:
            if self.splash_frames:
                self.splash = Explosion(self.x, self.y, self.splash_frames)
            else:
                self.alive = False
        if not (-4000 <= self.x <= 4800 and -4000 <= self.y <= 4600):
            self.alive = False

    def draw(self, screen, cam_x=0, cam_y=0):
        if self.splash:
            self.splash.draw(screen, cam_x, cam_y)
            return
        if not self.alive:
            return
        sx, sy = self.x - cam_x, self.y - cam_y
        rad = math.radians(self.angle)
        fx, fy = math.sin(rad), -math.cos(rad)
        rx, ry = math.cos(rad), math.sin(rad)
        corners = [
            (sx + fx*self.half_l + rx*self.half_w, sy + fy*self.half_l + ry*self.half_w),
            (sx + fx*self.half_l - rx*self.half_w, sy + fy*self.half_l - ry*self.half_w),
            (sx - fx*self.half_l - rx*self.half_w, sy - fy*self.half_l - ry*self.half_w),
            (sx - fx*self.half_l + rx*self.half_w, sy - fy*self.half_l + ry*self.half_w),
        ]
        pygame.draw.polygon(screen, self.color, corners)

    def hits(self, ship):
        if self.z > ship.deck_height:
            return False
        return math.hypot(self.x - ship.x, self.y - ship.y) < 20
    
    


def HEShell(x, y, z, launch_angle, angle):
    return Projectile(x, y, z, launch_angle, angle, damage=random.randint(40,50), color=(255, 180, 0))

def Light(x, y, z, launch_angle, angle):
    return Projectile(x, y, z, launch_angle, angle, damage=random.randint(2, 10), color=(0,0,0))

    