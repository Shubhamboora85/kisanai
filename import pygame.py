import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏎️ Turbo Road Racer")
clock = pygame.time.Clock()

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (80,  80,  80)
DKGRAY  = (50,  50,  50)
YELLOW  = (255, 220, 0)
RED     = (220, 50,  50)
GREEN   = (50,  200, 80)
BLUE    = (50,  120, 220)
ORANGE  = (255, 140, 0)
CYAN    = (0,   220, 220)
LGREEN  = (34,  139, 34)
ROADCOL = (60,  60,  60)
LINECOL = (240, 240, 0)
BGCOL   = (30,  160, 50)

font_big   = pygame.font.SysFont("Arial", 48, bold=True)
font_med   = pygame.font.SysFont("Arial", 30, bold=True)
font_small = pygame.font.SysFont("Arial", 22)

ROAD_LEFT  = 180
ROAD_RIGHT = 620
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANE_W     = ROAD_W // 4

CAR_COLORS = [RED, BLUE, ORANGE, CYAN, (180,0,180), (0,180,180)]

class PlayerCar:
    def __init__(self):
        self.w = 40
        self.h = 70
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 120
        self.speed = 0
        self.max_speed = 8
        self.boost_speed = 14
        self.fuel = 100.0
        self.boosting = False
        self.crashed = False
        self.crash_timer = 0
        self.crash_particles = []
        self.color = GREEN
        self.angle = 0

    def draw(self, surface):
        if self.crashed:
            for p in self.crash_particles:
                pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), int(p['r']))
            return
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        body = pygame.Rect(self.x + 4, self.y + 8, self.w - 8, self.h - 16)
        pygame.draw.rect(surface, self.color, body, border_radius=6)
        pygame.draw.rect(surface, (20, 20, 20), body, 2, border_radius=6)
        pygame.draw.rect(surface, (180, 230, 255), (self.x+8, self.y+12, self.w-16, 16), border_radius=3)
        pygame.draw.rect(surface, (180, 230, 255), (self.x+8, self.y+self.h-28, self.w-16, 14), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x, self.y+10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x+self.w-8, self.y+10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x, self.y+self.h-28, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x+self.w-8, self.y+self.h-28, 8, 18), border_radius=3)
        if self.boosting:
            for i in range(3):
                fx = self.x + 10 + i*10 + random.randint(-3,3)
                fy = self.y + self.h + random.randint(5,20)
                pygame.draw.circle(surface, ORANGE, (fx, fy), random.randint(4,8))
                pygame.draw.circle(surface, YELLOW, (fx, fy), random.randint(2,4))

    def update(self, keys):
        if self.crashed:
            self.crash_timer -= 1
            for p in self.crash_particles:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.3
                p['r'] = max(0, p['r'] - 0.15)
            return

        self.boosting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        top_speed = self.boost_speed if self.boosting else self.max_speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + 0.4, top_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - 0.5, -3)
        else:
            self.speed = max(self.speed - 0.2, 0)

        move_speed = 5 if not self.boosting else 7
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += move_speed

        self.x = max(ROAD_LEFT + 5, min(ROAD_RIGHT - self.w - 5, self.x))

        fuel_use = 0.03 if not self.boosting else 0.09
        self.fuel = max(0, self.fuel - fuel_use)
        if self.fuel == 0:
            self.speed = max(self.speed - 0.3, 0)

    def do_crash(self):
        self.crashed = True
        self.crash_timer = 90
        self.speed = 0
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        colors = [RED, ORANGE, YELLOW, WHITE, (200,200,200)]
        for _ in range(40):
            self.crash_particles.append({
                'x': cx, 'y': cy,
                'vx': random.uniform(-5,5),
                'vy': random.uniform(-8,1),
                'r': random.uniform(4,10),
                'color': random.choice(colors)
            })

    def rect(self):
        return pygame.Rect(self.x+4, self.y+8, self.w-8, self.h-16)


class TrafficCar:
    def __init__(self, speed_offset=0):
        lane = random.randint(0, 3)
        self.w = 40
        self.h = 70
        self.x = ROAD_LEFT + lane * LANE_W + (LANE_W - self.w) // 2
        self.y = -self.h - random.randint(0, 200)
        self.speed = random.uniform(2, 4) + speed_offset
        self.color = random.choice(CAR_COLORS)

    def update(self, road_speed):
        self.y += road_speed + self.speed

    def draw(self, surface):
        body = pygame.Rect(self.x+4, self.y+8, self.w-8, self.h-16)
        pygame.draw.rect(surface, self.color, body, border_radius=6)
        pygame.draw.rect(surface, (20,20,20), body, 2, border_radius=6)
        pygame.draw.rect(surface, (180,230,255), (self.x+8, self.y+12, self.w-16, 16), border_radius=3)
        pygame.draw.rect(surface, (180,230,255), (self.x+8, self.y+self.h-28, self.w-16, 14), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x, self.y+10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x+self.w-8, self.y+10, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x, self.y+self.h-28, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DKGRAY, (self.x+self.w-8, self.y+self.h-28, 8, 18), border_radius=3)

    def rect(self):
        return pygame.Rect(self.x+4, self.y+8, self.w-8, self.h-16)


class FuelPickup:
    def __init__(self):
        lane = random.randint(0, 3)
        self.x = ROAD_LEFT + lane * LANE_W + LANE_W//2 - 15
        self.y = -40
        self.w = 30
        self.h = 30
        self.collected = False

    def update(self, road_speed):
        self.y += road_speed + 1

    def draw(self, surface):
        if not self.collected:
            pygame.draw.rect(surface, ORANGE, (self.x, self.y, self.w, self.h), border_radius=8)
            pygame.draw.rect(surface, YELLOW, (self.x+3, self.y+3, self.w-6, self.h-6), border_radius=5)
            txt = font_small.render("⛽", True, BLACK)
            surface.blit(txt, (self.x+3, self.y+3))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


def draw_road(surface, offset):
    pygame.draw.rect(surface, BGCOL, (0, 0, WIDTH, HEIGHT))
    pygame.draw.rect(surface, ROADCOL, (ROAD_LEFT, 0, ROAD_W, HEIGHT))
    pygame.draw.rect(surface, (100,100,100), (ROAD_LEFT, 0, 6, HEIGHT))
    pygame.draw.rect(surface, (100,100,100), (ROAD_RIGHT-6, 0, 6, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_LEFT, 0, 4, HEIGHT))
    pygame.draw.rect(surface, WHITE, (ROAD_RIGHT-4, 0, 4, HEIGHT))
    dash_h = 40
    gap = 30
    total = dash_h + gap
    for lane in range(1, 4):
        lx = ROAD_LEFT + lane * LANE_W
        start = int(offset % total) - total
        y = start
        while y < HEIGHT:
            pygame.draw.rect(surface, LINECOL, (lx-2, y, 4, dash_h))
            y += total
    for tx in [ROAD_LEFT - 40, ROAD_LEFT - 70, ROAD_RIGHT + 20, ROAD_RIGHT + 50]:
        ty = int(offset * 0.3) % 120
        while ty < HEIGHT:
            pygame.draw.circle(surface, LGREEN, (tx, ty), 18)
            pygame.draw.circle(surface, (20,100,20), (tx, ty), 14)
            ty += 120


def draw_hud(surface, score, fuel, level, speed, boosting, high_score):
    bar_w = 200
    bar_h = 18
    fuel_pct = fuel / 100.0

    pygame.draw.rect(surface, DKGRAY, (20, 20, bar_w, bar_h), border_radius=5)
    fuel_color = GREEN if fuel_pct > 0.4 else (ORANGE if fuel_pct > 0.2 else RED)
    pygame.draw.rect(surface, fuel_color, (20, 20, int(bar_w * fuel_pct), bar_h), border_radius=5)
    pygame.draw.rect(surface, WHITE, (20, 20, bar_w, bar_h), 2, border_radius=5)
    flabel = font_small.render(f"⛽ Fuel: {int(fuel)}%", True, WHITE)
    surface.blit(flabel, (25, 22))

    score_txt = font_med.render(f"Score: {score}", True, YELLOW)
    surface.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 12))

    level_txt = font_small.render(f"Level {level}", True, WHITE)
    surface.blit(level_txt, (WIDTH - 110, 12))

    spd = int(speed * 20)
    spd_txt = font_small.render(f"Speed: {spd} km/h", True, WHITE)
    surface.blit(spd_txt, (WIDTH - 160, 38))

    hi_txt = font_small.render(f"Best: {high_score}", True, CYAN)
    surface.blit(hi_txt, (WIDTH - 130, 65))

    if boosting:
        boost_txt = font_med.render("⚡ BOOST!", True, YELLOW)
        surface.blit(boost_txt, (WIDTH//2 - boost_txt.get_width()//2, HEIGHT - 50))


def draw_menu(surface, high_score):
    surface.fill((10, 10, 30))
    title = font_big.render("🏎️ TURBO ROAD RACER", True, YELLOW)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 120))
    lines = [
        ("Arrow Keys / WASD", "Move car"),
        ("SHIFT", "Boost (uses fuel fast!)"),
        ("Collect ⛽", "Refuel your car"),
        ("Avoid traffic", "Don't crash!"),
    ]
    for i, (key, desc) in enumerate(lines):
        k = font_small.render(key, True, CYAN)
        d = font_small.render(f"→  {desc}", True, WHITE)
        surface.blit(k,  (200, 230 + i*38))
        surface.blit(d,  (420, 230 + i*38))

    hi = font_med.render(f"Best Score: {high_score}", True, ORANGE)
    surface.blit(hi, (WIDTH//2 - hi.get_width()//2, 400))

    blink = pygame.time.get_ticks() // 500 % 2 == 0
    if blink:
        start = font_med.render("Press SPACE or ENTER to Start!", True, GREEN)
        surface.blit(start, (WIDTH//2 - start.get_width()//2, 470))


def draw_gameover(surface, score, high_score):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0,0,0,170))
    surface.blit(ov, (0,0))
    go = font_big.render("GAME OVER", True, RED)
    surface.blit(go, (WIDTH//2 - go.get_width()//2, 180))
    sc = font_med.render(f"Your Score: {score}", True, YELLOW)
    surface.blit(sc, (WIDTH//2 - sc.get_width()//2, 270))
    hi = font_med.render(f"Best Score: {high_score}", True, CYAN)
    surface.blit(hi, (WIDTH//2 - hi.get_width()//2, 320))
    rs = font_med.render("Press R to Restart  |  ESC to Quit", True, WHITE)
    surface.blit(rs, (WIDTH//2 - rs.get_width()//2, 400))


def main():
    state = "menu"
    high_score = 0
    road_offset = 0
    score = 0
    level = 1
    traffic = []
    fuels = []
    spawn_timer = 0
    fuel_timer = 0
    player = PlayerCar()
    crash_restart_timer = 0

    while True:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        state = "playing"
                        player = PlayerCar()
                        traffic = []
                        fuels = []
                        score = 0
                        level = 1
                        road_offset = 0
                        spawn_timer = 0
                        fuel_timer = 0
                if state == "gameover":
                    if event.key == pygame.K_r:
                        state = "menu"
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                if event.key == pygame.K_ESCAPE and state == "playing":
                    state = "menu"

        if state == "menu":
            draw_menu(screen, high_score)
            pygame.display.flip()
            continue

        if state == "gameover":
            draw_road(screen, road_offset)
            draw_gameover(screen, score, high_score)
            pygame.display.flip()
            continue

        road_speed = 4 + level * 0.8 + (player.speed * 0.5)
        if player.boosting and not player.crashed:
            road_speed += 4

        if not player.crashed:
            player.update(keys)
            road_offset += road_speed
            score += 1 + (1 if player.boosting else 0)
            level = 1 + score // 800

        spawn_timer -= 1
        if spawn_timer <= 0:
            gap = max(20, 60 - level * 4)
            spawn_timer = random.randint(gap, gap + 30)
            traffic.append(TrafficCar(speed_offset=level*0.3))

        fuel_timer -= 1
        if fuel_timer <= 0:
            fuel_timer = random.randint(300, 500)
            fuels.append(FuelPickup())

        for t in traffic:
            t.update(road_speed)
        traffic = [t for t in traffic if t.y < HEIGHT + 100]

        for f in fuels:
            f.update(road_speed)
        fuels = [f for f in fuels if f.y < HEIGHT + 60]

        if not player.crashed:
            pr = player.rect()
            for t in traffic:
                if pr.colliderect(t.rect()):
                    player.do_crash()
                    break
            for f in fuels:
                if not f.collected and pr.colliderect(f.rect()):
                    f.collected = True
                    player.fuel = min(100, player.fuel + 35)

        fuels = [f for f in fuels if not f.collected]

        if player.crashed:
            crash_restart_timer += 1
            if crash_restart_timer > 120:
                crash_restart_timer = 0
                high_score = max(high_score, score)
                state = "gameover"
        else:
            crash_restart_timer = 0

        if player.fuel == 0 and player.speed == 0 and not player.crashed:
            high_score = max(high_score, score)
            state = "gameover"

        draw_road(screen, road_offset)
        for t in traffic:
            t.draw(screen)
        for f in fuels:
            f.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, player.fuel, level, road_speed, player.boosting and not player.crashed, high_score)

        if player.fuel <= 20 and not player.crashed:
            warn = font_med.render("⚠ LOW FUEL!", True, RED)
            if pygame.time.get_ticks() // 400 % 2 == 0:
                screen.blit(warn, (WIDTH//2 - warn.get_width()//2, HEIGHT - 90))

        pygame.display.flip()


if __name__ == "__main__":
    main()