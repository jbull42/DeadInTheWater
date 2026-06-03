import math

_GRAVITY = 0.1  # must match Projectile.gravity

def calculate_recommended_elevation_angle(enemy_distance, projectile_speed, ship):
    deck_height = ship.deck_height
    barrel_length = ship.turret.barrel_length

    def landing_range(pitch):
        z_init = deck_height + barrel_length * math.sin(pitch)
        vz = projectile_speed * math.sin(pitch)
        hz = projectile_speed * math.cos(pitch)
        disc = vz**2 + 2 * _GRAVITY * z_init
        if disc < 0:
            return 0
        t = (vz + math.sqrt(disc)) / _GRAVITY
        return hz * t

    low  = math.radians(-5)   # max downward, matches turret minimum
    high =  math.pi / 3   # steep upward,  range ≈ 7800 px

    if enemy_distance <= landing_range(low):
        return low
    if enemy_distance >= landing_range(high):
        return high

    for _ in range(60):
        mid = (low + high) / 2
        if landing_range(mid) < enemy_distance:
            low = mid
        else:
            high = mid

    return (low + high) / 2


