import math
import pygame
from classes.projectile import Projectile, HEShell, Light
from classes.explosion import Explosion
import random
from util import fire_control

class Turret:
    def __init__(self):
        self.bearing_angle = 0
        self.turn_rate = 0.0025
        self.cooldown = 0
        self.ap_fire_rate    = 80
        self.he_fire_rate    = 200
        self.light_fire_rate = 15
        self.projectiles = []
        self.firing = False
        self.ammo     = {"light": 30, "ap": 15, "he": 8}
        self.max_ammo = {"light": 30, "ap": 15, "he": 8}
        self.armed = "ap"
        self.elevation_angle = 0
        self.elevation_rate = 0.0005
        self.accuracy = 0

        self.time = 0
        self.barrel_length = 25
        self.gun_height = 25
        self.effects = []
        self.muzzle_frames       = None
        self.light_muzzle_frames = None
        self.hit_frames          = None
        self.light_hit_frames    = None
        self.splash_frames       = None


    def update(self, keys, ship_x, ship_y, screen_width, screen_height, ships, ship, ship_heading=0):
        self.time += 1

        if keys[pygame.K_LEFT]:
            self.bearing_angle -= self.turn_rate
        if keys[pygame.K_RIGHT]:
            self.bearing_angle += self.turn_rate
        if keys[pygame.K_UP]:
            self.elevation_angle = min(self.elevation_angle + self.elevation_rate, math.pi / 2)
        if keys[pygame.K_DOWN]:
            self.elevation_angle = max(self.elevation_angle - self.elevation_rate, math.radians(-5))

        if self.cooldown > 0:
            self.cooldown -= 1

        if keys[pygame.K_SPACE] and self.cooldown == 0 and self.ammo[self.armed] > 0:
            self.shoot(ship_x, ship_y)

        for p in self.projectiles:
            p.update(screen_width, screen_height)

        self.check_hits(ships)

    def update_ai(self, ship_x, ship_y, ships, ai):
        self.time += 1

        if self.cooldown > 0:
            self.cooldown -= 1

        PROJECTILE_SPEED = 30
        # Aim at player
        if ai.player:
            dx = ai.player.x - ship_x
            dy = ai.player.y - ship_y
            self.bearing_angle = math.atan2(dx, -dy)
            distance = math.hypot(dx, dy)
            self.elevation_angle = random.gauss(fire_control.calculate_recommended_elevation_angle(distance, PROJECTILE_SPEED, ai.player), 0.09)

        # Fire at scheduled times
        if ai.shoot_times and self.cooldown == 0 and self.ammo[self.armed] > 0:
            if self.time >= ai.shoot_times[0]:
                ai.shoot_times.pop(0)
                self.shoot(ship_x, ship_y, angle_offset=random.gauss(0, 1))

        for p in self.projectiles:
            p.update(800, 600)

        targets = ships + ([ai.player] if ai.player else [])
        self.check_hits(targets)

    def shoot(self, ship_x, ship_y, angle_offset=0):
        match self.armed:
            case 'he':    cls = HEShell
            case 'light': cls = Light
            case _:       cls = Projectile

        tip_x = ship_x + math.sin(self.bearing_angle) * self.barrel_length
        tip_y = ship_y - math.cos(self.bearing_angle) * self.barrel_length
        z_init = self.barrel_length * math.sin(self.elevation_angle) + self.gun_height
        angle_deg = math.degrees(self.bearing_angle) + angle_offset
        self.projectiles.append(cls(tip_x, tip_y, z_init, self.elevation_angle, angle_deg))

        if self.armed == 'ap':
            self.cooldown = self.ap_fire_rate
        elif self.armed == 'light':
            self.cooldown = self.light_fire_rate
        else:
            self.cooldown = self.he_fire_rate

        self.ammo[self.armed] -= 1
        self.projectiles[-1].hit_frames    = self.light_hit_frames if self.armed == 'light' else self.hit_frames
        self.projectiles[-1].splash_frames = self.splash_frames
        self.firing = True
        flash = self.light_muzzle_frames if self.armed == 'light' else self.muzzle_frames
        if flash:
            rotated = [pygame.transform.rotate(f, -math.degrees(self.bearing_angle)) for f in flash]
            self.effects.append(Explosion(tip_x, tip_y, rotated))


    def draw(self, screen, x, y, cam_x=0, cam_y=0):
        sx, sy = x - cam_x, y - cam_y
        rad = self.bearing_angle
        self.end = (int(sx + math.sin(rad) * self.barrel_length), int(sy - math.cos(rad) * self.barrel_length))

        for p in self.projectiles:
            p.draw(screen, cam_x, cam_y)
        self.projectiles = [p for p in self.projectiles if p.alive]

        self.firing = False

        for fx in self.effects:
            fx.update()
            fx.draw(screen, cam_x, cam_y)
        self.effects = [fx for fx in self.effects if fx.alive]


    def check_hits(self, ships):
        for p in self.projectiles:
            if not p.alive:
                continue
            for ship in ships:
                if p.hits(ship):
                    ship.take_hit()
                    ship.health -= p.damage
                    p.alive = False
                    frames = getattr(p, 'hit_frames', None) or self.hit_frames
                    if frames:
                        ship.effects.append(Explosion(p.x, p.y, frames))
