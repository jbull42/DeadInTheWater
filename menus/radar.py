import pygame
import math

BLIP_LIFETIME = 220  # frames a blip stays visible after detection

class Radar:

    def __init__(self, screen, position):
        self.screen = screen

        self.center = (screen.get_width() - 120, 120)
        self.radius = 100

        self.angle = 0
        self.speed = 1.3

        self.blips = []  # each entry: [radar_x, radar_y, lifetime, ship]
        self.selected_ship = None

        self.ship_position = position
        self.turret_angle = 0

        self.BACKGROUND_COLOR = (1, 31, 26)
        self.RADAR_COLOR = (2, 209, 188)

    def update(self, ships, turret_angle=0):
        self.turret_angle = turret_angle
        self.angle = (self.angle + self.speed) % 360

        cx, cy = self.ship_position
        radar_rad = math.radians(self.angle)

        # age existing blips, drop expired ones
        self.blips = [b for b in self.blips if b[2] > 0]
        for b in self.blips:
            b[2] -= 1

        for ship in ships:
            dx = ship.x - cx
            dy = ship.y - cy

            ship_angle = math.atan2(dy, dx)
            diff = abs((radar_rad - ship_angle + math.pi) % (2 * math.pi) - math.pi)

            if diff < math.radians(5):
                scale = 0.05# 0.1
                radar_x = self.center[0] + dx * scale
                radar_y = self.center[1] + dy * scale

                if math.hypot(radar_x - self.center[0], radar_y - self.center[1]) > self.radius:
                    continue

                # refresh existing blip nearby or add new one
                for b in self.blips:
                    if math.hypot(b[0] - radar_x, b[1] - radar_y) < 6:
                        b[0] = radar_x
                        b[1] = radar_y
                        b[2] = BLIP_LIFETIME
                        b[3] = ship
                        break
                else:
                    self.blips.append([radar_x, radar_y, BLIP_LIFETIME, ship])

        self.draw()

    def draw(self):
        cx, cy = self.center

        pygame.draw.circle(self.screen, self.BACKGROUND_COLOR, self.center, self.radius)
        pygame.draw.circle(self.screen, self.RADAR_COLOR, self.center, self.radius,       width=2)
        pygame.draw.circle(self.screen, self.RADAR_COLOR, self.center, self.radius * 2 // 3, width=1)
        pygame.draw.circle(self.screen, self.RADAR_COLOR, self.center, self.radius // 3,  width=1)

        # sweep line
        rad = math.radians(self.angle)
        end_x = cx + math.cos(rad) * self.radius
        end_y = cy + math.sin(rad) * self.radius
        pygame.draw.line(self.screen, self.RADAR_COLOR, self.center, (end_x, end_y), width=2)

        # blips — unfilled squares that fade with age
        for radar_x, radar_y, lifetime, ship in self.blips:
            selected = ship is self.selected_ship
            factor = max(0.25, lifetime / BLIP_LIFETIME)
            color = (255, 255, 80) if selected else (
                int(self.RADAR_COLOR[0] * factor),
                int(self.RADAR_COLOR[1] * factor),
                int(self.RADAR_COLOR[2] * factor),
            )
            size = 6 if selected else 4

            if ship.frnd == 'friend':
                pygame.draw.rect(
                    self.screen, color,
                    (int(radar_x) - size, int(radar_y) - size, size * 2, size * 2),
                    2 if selected else 1
                )
            elif ship.frnd == 'enemy':
                points = ((int(radar_x) - 5, int(radar_y) + 2.8868),
                          (int(radar_x) + 5, int(radar_y) + 2.8868),
                          (int(radar_x), int(radar_y) - 5.7735))
                pygame.draw.polygon(
                    self.screen,
                    color,
                    points,
                    width=1
                )

        # turret direction arrow
        yaw = self.turret_angle
        L = self.radius - 10
        head_l, head_w = 12, 6
        tip_x  = cx + math.sin(yaw) * L
        tip_y  = cy - math.cos(yaw) * L
        base_x = cx + math.sin(yaw) * (L - head_l)
        base_y = cy - math.cos(yaw) * (L - head_l)
        pygame.draw.line(self.screen, (220, 40, 40), (cx, cy), (int(tip_x), int(tip_y)), 2)
        pygame.draw.polygon(self.screen, (220, 40, 40), [
            (int(tip_x), int(tip_y)),
            (int(base_x + math.cos(yaw) * head_w), int(base_y + math.sin(yaw) * head_w)),
            (int(base_x - math.cos(yaw) * head_w), int(base_y - math.sin(yaw) * head_w)),
        ])

    def ship_at_click(self, mx, my):
        for b in self.blips:
            if math.hypot(mx - b[0], my - b[1]) < 10:
                return b[3]
        return None
