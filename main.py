import pygame
from classes.ship import Ship
from classes.ai import AI
from buttons.button import Button
import math
from util.fire_control import calculate_recommended_elevation_angle
from levels.level_1 import LEVEL

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_W, SCREEN_H = screen.get_size()
clock = pygame.time.Clock()
font       = pygame.font.Font('fonts/Righteous-Regular.ttf', 20)
font_large = pygame.font.Font('fonts/Righteous-Regular.ttf', 60)
font_small = pygame.font.Font('fonts/Righteous-Regular.ttf', 22)
font_tiny  = pygame.font.Font('fonts/Righteous-Regular.ttf', 15)

# --- ship catalogue (name, avatar path, stats) ---
SHIP_CATALOGUE = [
    {
        'name':   'IJN Yamato',
        'avatar': pygame.transform.scale(
                      pygame.image.load('sprites/yamato.png').convert_alpha(),
                      (180, 180)
                  ),
        'stats':  ['Nationality: Japanese', 'Speed: 0.25', 'Health: 100', 'AP shells: 10', 'HE shells: 5', 'Main Armament: 18"'],
    },
    {
        'name':   'USS Iowa',
        'avatar': pygame.transform.scale(
                      pygame.image.load('sprites/iowa.png').convert_alpha(),
                      (180, 180)
                  ),
        'stats':  ['Nationality: American', 'Speed: 0.25', 'Health: 100', 'AP shells: 10', 'HE shells: 5', 'Main Armament: 16"'],
    },
]

selected_ship_index = 0   # index into SHIP_CATALOGUE

# explosion sprite sheet: 7 frames × 32 px wide
_expl_sheet = pygame.image.load('sprites/explosion.png').convert_alpha()
_expl_raw   = [_expl_sheet.subsurface((i * 32, 0, 32, 32)) for i in range(7)]
hit_frames         = [pygame.transform.scale(f, (72, 72))   for f in _expl_raw]
light_hit_frames   = [pygame.transform.scale(f, (32, 32))   for f in _expl_raw]
death_frames       = [pygame.transform.scale(f, (180, 180)) for f in _expl_raw]

# muzzle flash sprite sheet: 7 frames × 128 px wide
_muzz_sheet         = pygame.image.load('sprites/muzzle_flash.png').convert_alpha()
_muzz_raw           = [_muzz_sheet.subsurface((i * 128, 0, 128, 128)) for i in range(7)]
muzzle_frames       = [pygame.transform.scale(f, (48, 48)) for f in _muzz_raw]
light_muzzle_frames = [pygame.transform.scale(f, (22, 22)) for f in _muzz_raw]

# water splash sprite sheet: 5 frames × 32 px wide
_splash_sheet = pygame.image.load('sprites/splash.png').convert_alpha()
_splash_raw   = [_splash_sheet.subsurface((i * 32, 0, 32, 32)) for i in range(5)]
splash_frames = [pygame.transform.scale(f, (20, 20)) for f in _splash_raw]

def apply_effects(s):
    s.turret.muzzle_frames       = muzzle_frames
    s.turret.light_muzzle_frames = light_muzzle_frames
    s.turret.hit_frames          = hit_frames
    s.turret.light_hit_frames    = light_hit_frames
    s.turret.splash_frames       = splash_frames
    s.hit_frames                 = hit_frames
    s.death_frames               = death_frames

CARD_W, CARD_H = 220, 330
CARD_Y = 130

def card_rect(i):
    total_w = len(SHIP_CATALOGUE) * CARD_W + (len(SHIP_CATALOGUE) - 1) * 20
    start_x = SCREEN_W // 2 - total_w // 2
    return pygame.Rect(start_x + i * (CARD_W + 20), CARD_Y, CARD_W, CARD_H)

# -----------------------------------------------

def draw_ammo_bars(surface, x, y, count, max_count, color, btn_width, bar_h=12, gap=2, rows=1):
    per_row = -(-max_count // rows)
    bar_w = max(4, (btn_width - (per_row - 1) * gap) // per_row)
    for i in range(max_count):
        col = i % per_row
        row = i // per_row
        bar_x = x + col * (bar_w + gap)
        bar_y = y - row * (bar_h + gap)
        c = color if i < count else (40, 55, 65)
        pygame.draw.rect(surface, c, (bar_x, bar_y, bar_w, bar_h))

def make_ships(player):
    result = []
    for cfg in LEVEL:
        s = Ship(cfg["x"], cfg["y"], False, screen, cfg["name"], frnd=cfg["frnd"])
        s.ai = AI(cfg["behavior"], cfg.get("shoot_times", []), cfg.get("waypoints", []))
        s.ai.player = player
        apply_effects(s)
        result.append(s)
    return result

def reset():
    global ship, ships, selected_enemy, state
    ship           = Ship(400, 300, True, screen, SHIP_CATALOGUE[selected_ship_index]['name'], frnd='friend')
    ship.sprite    = iowa_sprite
    apply_effects(ship)
    ships          = make_ships(ship)
    selected_enemy = None
    ship.radar.selected_ship = None
    state = 'menu'

running        = True
state          = 'menu'
selected_enemy = None

iowa_sprite = pygame.transform.scale(
    pygame.image.load('sprites/iowa_overhead.png').convert_alpha(),
    (60, 60)
)

ship = Ship(400, 300, True, screen, 'USS Iowa', frnd='friend')
ship.sprite = iowa_sprite
apply_effects(ship)
ships = make_ships(ship)

def arm_standard():
    ship.turret.armed = "ap"
    standard_btn.selected = True
    heavy_btn.selected = False
    light_btn.selected = False


def arm_heavy():
    ship.turret.armed = "he"
    standard_btn.selected = False
    heavy_btn.selected = True
    light_btn.selected = False


def arm_light():
    ship.turret.armed = 'light'
    standard_btn.selected = False
    heavy_btn.selected = False
    light_btn.selected = True

def arm_port():
    ship.torpedo_side = "port"
    port_btn.selected = True
    stbd_btn.selected = False

def arm_stbd():
    ship.torpedo_side = "starboard"
    port_btn.selected = False
    stbd_btn.selected = True

light_btn = Button(x=12, y=SCREEN_H - 42, width=100, height=30, text='LIGHT', action=arm_light)
standard_btn = Button(x=120,  y=SCREEN_H - 42, width=100, height=30, text="ARMOR PIERCING", action=arm_standard)
heavy_btn    = Button(x=240, y=SCREEN_H - 42, width=100, height=30, text="HIGH EXPLOSIVE", action=arm_heavy)
port_btn     = Button(x=350, y=SCREEN_H - 42, width=90,  height=30, text="PORT TORP",      action=arm_port)
stbd_btn     = Button(x=450, y=SCREEN_H - 42, width=90,  height=30, text="STBD TORP",      action=arm_stbd)
standard_btn.selected = True
stbd_btn.selected = True

ammo_buttons = [light_btn, standard_btn, heavy_btn, port_btn, stbd_btn]


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if state == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i in range(len(SHIP_CATALOGUE)):
                    if card_rect(i).collidepoint(mx, my):
                        selected_ship_index = i
                # click SET SAIL button area
                sail_rect = pygame.Rect(SCREEN_W // 2 - 100, CARD_Y + CARD_H + 20, 200, 40)
                if sail_rect.collidepoint(mx, my):
                    state = 'game'
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                state = 'game'

        elif state == 'game':
            for btn in ammo_buttons:
                btn.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                ship.fire_torpedo()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if math.hypot(mx - (SCREEN_W - 120), my - 120) <= 100:
                    clicked = ship.radar.ship_at_click(mx, my)
                    selected_enemy = clicked
                    ship.radar.selected_ship = clicked

        elif state == 'game_over':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset()

    # ── MENU ────────────────────────────────────────────────────────────
    if state == 'menu':
        screen.fill((0, 10, 25))

        title = font_large.render("Dead In The Water", True, (220, 200, 100))
        screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))

        sub = font_tiny.render("SELECT YOUR VESSEL", True, (100, 130, 150))
        screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 100))

        for i, entry in enumerate(SHIP_CATALOGUE):
            r = card_rect(i)
            selected = (i == selected_ship_index)

            # card background
            pygame.draw.rect(screen, (15, 35, 55), r, border_radius=4)
            border_color = (220, 190, 80) if selected else (50, 80, 110)
            pygame.draw.rect(screen, border_color, r, 2, border_radius=4)

            # avatar
            avatar = entry['avatar']
            ax = r.x + (CARD_W - avatar.get_width()) // 2
            screen.blit(avatar, (ax, r.y + 12))

            # ship name
            name_surf = font_small.render(entry['name'], True, (200, 220, 255))
            screen.blit(name_surf, (r.x + (CARD_W - name_surf.get_width()) // 2,
                                    r.y + avatar.get_height() + 7))

            # stats
            for j, stat in enumerate(entry['stats']):
                s = font_tiny.render(stat, True, (120, 150, 170))
                screen.blit(s, (r.x + 12, r.y + avatar.get_height() + 35 + j * 18))

        # SET SAIL button
        sail_rect = pygame.Rect(SCREEN_W // 2 - 100, CARD_Y + CARD_H + 20, 200, 40)
        mx, my = pygame.mouse.get_pos()
        sail_color = (40, 90, 60) if sail_rect.collidepoint(mx, my) else (25, 65, 45)
        pygame.draw.rect(screen, sail_color, sail_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 180, 110), sail_rect, 2, border_radius=4)
        sail_text = font_small.render("SET SAIL", True, (180, 240, 190))
        screen.blit(sail_text, (sail_rect.centerx - sail_text.get_width() // 2,
                                sail_rect.centery - sail_text.get_height() // 2))

        hint = font_tiny.render("click a ship  ·  press Enter to start", True, (60, 80, 90))
        screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 30))

    # ── GAME ────────────────────────────────────────────────────────────
    elif state == 'game':
        screen.fill((0, 33, 48))

        if len(ships) == 0:
            state = 'game_over'

        keys = pygame.key.get_pressed()

        cam_x = int(ship.x - SCREEN_W // 2)
        cam_y = int(ship.y - SCREEN_H // 2)

        for boat in ships + [ship]:
            if not boat.alive:
                ships = [s for s in ships if s != boat]
            boat.update(keys, ships, cam_x, cam_y)

        target = selected_enemy if selected_enemy in ships else None

        cooldown_secs = ship.turret.cooldown / 60
        armed = ship.turret.armed
        current_ammo = ship.turret.ammo[armed]
        if current_ammo == 0:
            cooldown_text = "OUT OF AMMO"
        elif cooldown_secs == 0:
            cooldown_text = "READY"
        else:
            cooldown_text = f"{cooldown_secs:.1f}s"

        if target is not None:
            target_distance = math.hypot(target.x - ship.x, target.y - ship.y)
            recommended_elevation_angle = calculate_recommended_elevation_angle(target_distance, 30, ship)
            elevation_offset = (ship.turret.elevation_angle * 180 / math.pi) - math.degrees(recommended_elevation_angle)
            target_lines = [
                f"Target: {target.name}",
                f"Target Speed: {target.speed:.2f}",
                f"Target Heading: {target.heading:.1f}°",
                f"Target Distance: {target_distance:.1f}",
                f"Elevation Offset: +{elevation_offset:.1f}°" if elevation_offset > 0 else f"Elevation Offset: {elevation_offset:.1f}°",
            ]
        else:
            target_lines = [
                "Target: ---", "Target Speed: ---", "Target Heading: ---",
                "Target Distance: ---", "Elevation Offset: ---",
            ]

        hud_lines = [
            f"Armed: {'Light' if armed == 'light' else 'Armor Piercing' if armed == 'ap' else 'High Explosive'}",
            f"Cooldown: {cooldown_text}",
            f"Speed: {ship.speed:.1f}",
            f"Heading: {ship.heading:.1f}°",
            *target_lines,
            f"Turret Elevation: {(ship.turret.elevation_angle * 180 / math.pi):.1f}°",
            f"Turret Bearing: {(ship.turret.bearing_angle * 180 / math.pi):.1f}°"
        ]
        for i, line in enumerate(hud_lines):
            surface = font.render(line, True, (180, 200, 220))
            screen.blit(surface, (SCREEN_W - surface.get_width() - 12,
                                  SCREEN_H - 170 - (len(hud_lines) - i) * 20))

        for btn in ammo_buttons:
            btn.draw(screen)

        bar_y = SCREEN_H - 58
        draw_ammo_bars(screen,  12, bar_y, ship.turret.ammo['light'],       ship.turret.max_ammo['light'], (100, 180, 255), 100, rows=2)
        draw_ammo_bars(screen, 120, bar_y, ship.turret.ammo['ap'],          ship.turret.max_ammo['ap'],    (160, 170, 200), 100)
        draw_ammo_bars(screen, 240, bar_y, ship.turret.ammo['he'],          ship.turret.max_ammo['he'],    (230, 140,  40), 100)
        draw_ammo_bars(screen, 350, bar_y, ship.torpedo_ammo['port'],       ship.max_torpedo_ammo,         ( 80, 210, 170),  90)
        draw_ammo_bars(screen, 450, bar_y, ship.torpedo_ammo['starboard'],  ship.max_torpedo_ammo,         ( 80, 210, 170),  90)

    # ── GAME OVER ────────────────────────────────────────────────────────
    elif state == 'game_over':
        screen.fill((0, 10, 20))

        title    = font_large.render("VICTORY",               True, (220, 200, 100))
        subtitle = font_small.render("All enemies destroyed", True, (160, 180, 160))
        prompt   = font_small.render("Press R to play again", True, (120, 140, 160))

        screen.blit(title,    (SCREEN_W // 2 - title.get_width() // 2,    SCREEN_H // 2 - 100))
        screen.blit(subtitle, (SCREEN_W // 2 - subtitle.get_width() // 2, SCREEN_H // 2 - 10))
        screen.blit(prompt,   (SCREEN_W // 2 - prompt.get_width() // 2,   SCREEN_H // 2 + 40))

    pygame.display.flip()
    clock.tick(60)
