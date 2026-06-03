import math
import pygame
from classes.turret import Turret
from classes.torpedo import Torpedo
from classes.explosion import Explosion
from menus.radar import Radar

class Ship:
    def __init__(self, x, y, player_controlled, screen, name, frnd, speed=0):
        self.x = x
        self.y = y
        self.heading = 0
        self.speed = speed
        self.turn_rate = 0.1
        self.max_speed = 0.25
        self.min_speed = -0.25
        self.deck_height = 25
        self.turret = Turret()
        self.turret.gun_height = self.deck_height
        self.player_controlled = player_controlled
        self.health = 100
        self.name = name
        self.frnd = frnd

        self.distance = 0

        self.font = pygame.font.Font('fonts/Righteous-Regular.ttf', 13)

        self.radar_angle = 0
        self.radar_speed = 10
        self.blips = []

        self.alive = True
        self.dying = False
        self.alpha = 255
        self.effects = []
        self.hit_frames = None
        self.death_frames = None
        self.sprite = None
        self.cam_x = 0
        self.cam_y = 0
        self.wake = []
        self.max_wake = 120
        self._wake_tick = 0
        self.torpedoes = []
        self.torpedo_side = "starboard"
        self.torpedo_ammo     = {"port": 4, "starboard": 4}
        self.max_torpedo_ammo = 4

        self.screen = screen
        self.radar = Radar(screen, (self.x, self.y))
        self.ai = None
        

    def draw(self, screen):
        self.screen = screen
        self.radar.screen = screen

        if self.dying:
            temp = pygame.Surface(screen.get_size())
            temp.fill((3, 3, 7))
            temp.set_colorkey((3, 3, 7))
            self._draw_to(temp)
            temp.set_alpha(self.alpha)
            screen.blit(temp, (0, 0))
        else:
            self._draw_to(screen)

        for fx in self.effects:
            fx.update()
            fx.draw(screen, self.cam_x, self.cam_y)
        self.effects = [fx for fx in self.effects if fx.alive]

    def _draw_to(self, surf):
        size = 20
        sx = self.x - self.cam_x
        sy = self.y - self.cam_y
        rad = math.radians(self.heading)

        points = [
            (sx + math.sin(rad) * size * 2.0,             sy - math.cos(rad) * size * 2.0),
            (sx + math.sin(rad + math.pi/2) * size * 0.2, sy - math.cos(rad + math.pi/2) * size * 0.2),
            (sx - math.sin(rad) * size * 1.0,             sy + math.cos(rad) * size * 1.0),
            (sx + math.sin(rad - math.pi/2) * size * 0.2, sy - math.cos(rad - math.pi/2) * size * 0.2),
        ]

        for i, (wx, wy) in enumerate(self.wake):
            t = i / max(1, len(self.wake) - 1)
            color = (int(20 + 200 * t), int(80 + 140 * t), int(100 + 130 * t))
            dot_size = max(1, int(3 * t))
            pygame.draw.circle(surf, color, (int(wx - self.cam_x), int(wy - self.cam_y)), dot_size)

        for torp in self.torpedoes:
            torp.draw(surf, self.cam_x, self.cam_y)
        self.torpedoes = [t for t in self.torpedoes if t.alive]

        if self.sprite:
            rotated = pygame.transform.rotate(self.sprite, -self.heading)
            r = rotated.get_rect(center=(sx, sy))
            surf.blit(rotated, r.topleft)
        else:
            pygame.draw.polygon(surf, (200, 220, 255), points)

        self.turret.draw(surf, self.x, self.y, self.cam_x, self.cam_y)

        half_h = self.sprite.get_height() // 2 if self.sprite else 30
        bar_y  = sy - half_h - 15
        name_y = sy + half_h + 8

        if not self.dying:
            pygame.draw.rect(surf, color=(10, 10, 10), rect=(sx - 25, bar_y, 50, 10))
            pygame.draw.rect(surf, color=(0, 200, 0),  rect=(sx - 25, bar_y, self.health * 50 / 100, 10))

        text_surface = self.font.render(self.name, True, (255, 255, 255))
        surf.blit(text_surface, (sx - 30, name_y))


        


    def update(self, keys, ships, cam_x=0, cam_y=0):
        self.cam_x = cam_x
        self.cam_y = cam_y

        if self.player_controlled:
            if keys[pygame.K_a]: self.heading -= self.turn_rate
            if keys[pygame.K_d]: self.heading += self.turn_rate
            if keys[pygame.K_w]: self.speed = min(self.speed + 0.002, self.max_speed)
            if keys[pygame.K_s]: self.speed = max(self.speed - 0.002, self.min_speed)
            self.turret.update(keys, self.x, self.y, 800, 600, ships, self, self.heading)
        elif self.ai:
            self.ai.update(self, ships)
            self.turret.update_ai(self.x, self.y, ships, self.ai)
        

        if self.health <= 0 and not self.dying:
            self.dying = True
            if self.death_frames:
                self.effects.append(Explosion(self.x, self.y, self.death_frames))

        if self.dying:
            self.alpha = max(0, self.alpha - 3)
            if self.alpha <= 0:
                self.alive = False
            self.draw(self.screen)
            return
    

        rad = math.radians(self.heading)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed

        self._wake_tick += 1
        stern_x = self.x - math.sin(rad) * 20
        stern_y = self.y + math.cos(rad) * 20
        if abs(self.speed) > 0.005:
            if self._wake_tick % 4 == 0:
                self.wake.append((stern_x, stern_y))
                if len(self.wake) > self.max_wake:
                    self.wake.pop(0)
        elif self.wake:
            self.wake.pop(0)

        for torp in self.torpedoes:
            torp.update(800, 600)
        for torp in self.torpedoes:
            if not torp.alive:
                continue
            for target in ships:
                if torp.hits(target):
                    target.health -= torp.damage
                    target.take_hit()
                    torp.alive = False
                    if self.hit_frames:
                        target.effects.append(Explosion(torp.x, torp.y, self.hit_frames))
                    break

        self.update_radar(ships, (self.x, self.y))

        self.draw(self.screen)

        

        

    def fire_torpedo(self):
        if self.torpedo_ammo[self.torpedo_side] <= 0:
            return
        rad = math.radians(self.heading)
        if self.torpedo_side == "starboard":
            angle = self.heading + 90
            spawn_x = self.x + math.cos(rad) * 15
            spawn_y = self.y + math.sin(rad) * 15
        else:
            angle = self.heading - 90
            spawn_x = self.x - math.cos(rad) * 15
            spawn_y = self.y - math.sin(rad) * 15
        self.torpedo_ammo[self.torpedo_side] -= 1
        self.torpedoes.append(Torpedo(spawn_x, spawn_y, angle))

    def take_hit(self):
        print('Hit!')

    def update_radar(self, ships, position):
        self.radar.update(ships, turret_angle=self.turret.bearing_angle)
        self.radar.ship_position = position
