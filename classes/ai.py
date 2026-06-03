import math


class AI:
    def __init__(self, behavior, shoot_times, waypoints=None):
        self.behavior = behavior
        self.waypoints = list(waypoints or [])
        self.waypoint_index = 0
        self.player = None  # set by main after ship creation
        self.shoot_times = list(shoot_times) if shoot_times is not None else []

    def update(self, ship, ships):
        if self.behavior == "patrol":
            self._patrol(ship)
        elif self.behavior == "chase":
            self._chase(ship)
        # "idle": no movement

    # ── behaviors ────────────────────────────────────────────────────────

    def _patrol(self, ship):
        if not self.waypoints:
            return
        tx, ty = self.waypoints[self.waypoint_index]
        dx, dy = tx - ship.x, ty - ship.y
        if math.hypot(dx, dy) < 20:
            self.waypoint_index = (self.waypoint_index + 1) % len(self.waypoints)
            return
        desired = math.degrees(math.atan2(dx, -dy))
        ship.heading = _steer(ship.heading, desired, rate=0.8)
        ship.speed = min(ship.speed + 0.002, ship.max_speed * 0.6)

    def _chase(self, ship):
        if not self.player:
            return
        dx, dy = self.player.x - ship.x, self.player.y - ship.y
        desired = math.degrees(math.atan2(dx, -dy))
        ship.heading = _steer(ship.heading, desired, rate=0.6)
        ship.speed = min(ship.speed + 0.002, ship.max_speed)


def _steer(current, desired, rate):
    diff = (desired - current + 180) % 360 - 180
    if abs(diff) <= rate:
        return desired
    return current + math.copysign(rate, diff)
