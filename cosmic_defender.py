import pygame
import random
import math
from collections import deque
import heapq

# =========================
# INITIALIZATION
# =========================

pygame.init()

WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COSMIC DEFENDER")

CLOCK = pygame.time.Clock()
FPS = 60

FONT = pygame.font.SysFont("consolas", 22)
BIG_FONT = pygame.font.SysFont("consolas", 48, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 16)

BLACK = (8, 10, 20)
WHITE = (240, 240, 255)
CYAN = (0, 220, 255)
RED = (255, 70, 90)
PURPLE = (160, 90, 255)
GREEN = (80, 255, 150)
YELLOW = (255, 220, 80)


# =========================
# LINKED LIST
# Used for floating messages
# =========================

class Node:
    def __init__(self, message, timer):
        self.message = message
        self.timer = timer
        self.next = None


class MessageList:
    def __init__(self):
        self.head = None

    def add(self, message, timer=120):
        new_node = Node(message, timer)

        if self.head is None:
            self.head = new_node
        else:
            current = self.head

            while current.next:
                current = current.next

            current.next = new_node

    def update(self):
        current = self.head
        previous = None

        while current:
            current.timer -= 1

            if current.timer <= 0:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

            else:
                previous = current

            current = current.next

    def draw(self):
        current = self.head
        y = 100

        while current:
            text = FONT.render(current.message, True, YELLOW)
            SCREEN.blit(text, (20, y))
            y += 30
            current = current.next


# =========================
# PLAYER
# =========================

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 80

        self.speed = 5
        self.health = 3

        self.shoot_cooldown = 0
        self.shield = 0

        self.width = 40
        self.height = 45

    def move(self, keys):

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.x = max(20, min(WIDTH - 20, self.x))
        self.y = max(20, min(HEIGHT - 20, self.y))

    def shoot(self, bullets):

        if self.shoot_cooldown == 0:

            bullets.append(
                Bullet(self.x, self.y - 20)
            )

            self.shoot_cooldown = 15

    def update(self):

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.shield > 0:
            self.shield -= 1

    def draw(self):

        points = [
            (self.x, self.y - 25),
            (self.x - 20, self.y + 20),
            (self.x, self.y + 10),
            (self.x + 20, self.y + 20)
        ]

        pygame.draw.polygon(SCREEN, CYAN, points)
        pygame.draw.polygon(SCREEN, WHITE, points, 2)

        # Shield effect
        if self.shield > 0:
            pygame.draw.circle(
                SCREEN,
                PURPLE,
                (self.x, self.y),
                35,
                2
            )

    def get_rect(self):

        return pygame.Rect(
            self.x - 20,
            self.y - 20,
            40,
            40
        )


# =========================
# BULLETS
# =========================

class Bullet:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.speed = 9

    def update(self):

        self.y -= self.speed

    def draw(self):

        pygame.draw.rect(
            SCREEN,
            CYAN,
            (self.x - 3, self.y - 10, 6, 15)
        )

        pygame.draw.circle(
            SCREEN,
            WHITE,
            (self.x, self.y),
            3
        )

    def get_rect(self):

        return pygame.Rect(
            self.x - 3,
            self.y - 10,
            6,
            15
        )


# =========================
# ENEMY
# =========================

class Enemy:

    def __init__(self, enemy_type="normal"):

        self.x = random.randint(40, WIDTH - 40)
        self.y = -40

        self.type = enemy_type

        if enemy_type == "fast":
            self.speed = 4
            self.health = 1
            self.color = YELLOW

        elif enemy_type == "heavy":
            self.speed = 1.5
            self.health = 3
            self.color = PURPLE

        else:
            self.speed = 2
            self.health = 1
            self.color = RED

        self.radius = 18

    def update(self, player):

        # Simple enemy movement
        direction = pygame.Vector2(
            player.x - self.x,
            player.y - self.y
        )

        if direction.length() > 0:
            direction = direction.normalize()

        self.x += direction.x * self.speed * 0.4
        self.y += self.speed

    def draw(self):

        pygame.draw.circle(
            SCREEN,
            self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

        pygame.draw.circle(
            SCREEN,
            WHITE,
            (int(self.x), int(self.y)),
            self.radius,
            2
        )

    def get_rect(self):

        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


# =========================
# POWERUP
# =========================

class PowerUp:

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.speed = 2

        self.type = random.choice(
            ["health", "shield", "rapid"]
        )

    def update(self):

        self.y += self.speed

    def draw(self):

        colors = {
            "health": GREEN,
            "shield": PURPLE,
            "rapid": YELLOW
        }

        pygame.draw.circle(
            SCREEN,
            colors[self.type],
            (int(self.x), int(self.y)),
            12
        )

        pygame.draw.circle(
            SCREEN,
            WHITE,
            (int(self.x), int(self.y)),
            12,
            2
        )

    def get_rect(self):

        return pygame.Rect(
            self.x - 12,
            self.y - 12,
            24,
            24
        )


# =========================
# PARTICLES
# =========================

class Particle:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)

        self.life = 30
        self.radius = random.randint(2, 5)

    def update(self):

        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):

        if self.life > 0:

            pygame.draw.circle(
                SCREEN,
                YELLOW,
                (int(self.x), int(self.y)),
                self.radius
            )


# =========================
# STARFIELD
# =========================

stars = []

for i in range(100):

    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])


def draw_stars():

    for star in stars:

        pygame.draw.circle(
            SCREEN,
            WHITE,
            (star[0], star[1]),
            star[2]
        )

        star[1] += star[2]

        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)


# =========================
# GAME VARIABLES
# =========================

player = Player()

bullets = []
enemies = []
powerups = []
particles = []

messages = MessageList()

score = 0
game_over = False

high_scores = []

# HASH MAP
statistics = {
    "enemies_destroyed": 0,
    "bullets_fired": 0,
    "powerups_collected": 0
}

# STACK
powerup_history = []

# QUEUE
enemy_spawn_queue = deque()

# PRIORITY QUEUE
scheduled_events = []

event_id = 0

spawn_timer = 0
powerup_timer = 0


# =========================
# DSA: SEARCHING
# Find nearest enemy
# =========================

def find_nearest_enemy():

    if not enemies:
        return None

    nearest = enemies[0]
    shortest_distance = float("inf")

    for enemy in enemies:

        distance = math.sqrt(
            (enemy.x - player.x) ** 2 +
            (enemy.y - player.y) ** 2
        )

        if distance < shortest_distance:

            shortest_distance = distance
            nearest = enemy

    return nearest


# =========================
# DSA: SORTING
# Sort leaderboard
# =========================

def update_leaderboard(new_score):

    high_scores.append(new_score)

    high_scores.sort(reverse=True)

    # Keep only top five
    del high_scores[5:]


# =========================
# RESET GAME
# =========================

def reset_game():

    global player, bullets, enemies
    global powerups, particles, score
    global game_over, spawn_timer
    global powerup_timer, statistics
    global powerup_history, enemy_spawn_queue
    global scheduled_events, event_id

    player = Player()

    bullets = []
    enemies = []
    powerups = []
    particles = []

    score = 0
    game_over = False

    spawn_timer = 0
    powerup_timer = 0

    statistics = {
        "enemies_destroyed": 0,
        "bullets_fired": 0,
        "powerups_collected": 0
    }

    powerup_history = []
    enemy_spawn_queue = deque()

    scheduled_events = []
    event_id = 0


# =========================
# DRAW HUD
# =========================

def draw_hud():

    score_text = FONT.render(
        f"SCORE: {score}",
        True,
        WHITE
    )

    health_text = FONT.render(
        f"HEALTH: {player.health}",
        True,
        GREEN
    )

    SCREEN.blit(score_text, (20, 20))
    SCREEN.blit(health_text, (WIDTH - 180, 20))

    pygame.draw.line(
        SCREEN,
        CYAN,
        (0, 55),
        (WIDTH, 55),
        2
    )


# =========================
# GAME OVER SCREEN
# =========================

def draw_game_over():

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 180))

    SCREEN.blit(overlay, (0, 0))

    title = BIG_FONT.render(
        "GAME OVER",
        True,
        RED
    )

    final_score = FONT.render(
        f"FINAL SCORE: {score}",
        True,
        WHITE
    )

    restart = FONT.render(
        "PRESS R TO RESTART",
        True,
        CYAN
    )

    quit_text = FONT.render(
        "PRESS ESC TO QUIT",
        True,
        WHITE
    )

    SCREEN.blit(
        title,
        title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    )

    SCREEN.blit(
        final_score,
        final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    )

    SCREEN.blit(
        restart,
        restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    )

    SCREEN.blit(
        quit_text,
        quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 90))
    )


# =========================
# MAIN GAME LOOP
# =========================

running = True

while running:

    CLOCK.tick(FPS)

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if game_over and event.key == pygame.K_r:
                reset_game()

    SCREEN.fill(BLACK)

    draw_stars()

    # =====================
    # GAME RUNNING
    # =====================

    if not game_over:

        keys = pygame.key.get_pressed()

        player.move(keys)

        if keys[pygame.K_SPACE]:

            player.shoot(bullets)

            statistics["bullets_fired"] += 1

        player.update()

        messages.update()

        # ENEMY SPAWNING
        spawn_timer += 1

        if spawn_timer >= max(20, 70 - score // 100):

            spawn_timer = 0

            # QUEUE
            enemy_spawn_queue.append(
                random.choice(["normal", "fast", "heavy"])
            )

        if enemy_spawn_queue:

            enemy_type = enemy_spawn_queue.popleft()

            enemies.append(
                Enemy(enemy_type)
            )

        # POWERUP SPAWNING
        powerup_timer += 1

        if powerup_timer >= 600:

            powerup_timer = 0

            powerups.append(
                PowerUp(
                    random.randint(30, WIDTH - 30),
                    -20
                )
            )

        # BULLETS
        for bullet in bullets[:]:

            bullet.update()

            if bullet.y < 0:
                bullets.remove(bullet)

        # ENEMIES
        for enemy in enemies[:]:

            enemy.update(player)

            # Enemy hits player
            if enemy.get_rect().colliderect(
                player.get_rect()
            ):

                if player.shield <= 0:

                    player.health -= 1

                    messages.add("SHIP DAMAGED!")

                enemies.remove(enemy)

                if player.health <= 0:

                    game_over = True

                    update_leaderboard(score)

                continue

            # Enemy escapes
            if enemy.y > HEIGHT:

                enemies.remove(enemy)

        # BULLET COLLISION
        for bullet in bullets[:]:

            for enemy in enemies[:]:

                if bullet.get_rect().colliderect(
                    enemy.get_rect()
                ):

                    bullets.remove(bullet)

                    enemy.health -= 1

                    # Enemy destroyed
                    if enemy.health <= 0:

                        enemies.remove(enemy)

                        score += 10

                        statistics[
                            "enemies_destroyed"
                        ] += 1

                        # PARTICLES
                        for i in range(8):

                            particles.append(
                                Particle(enemy.x, enemy.y)
                            )

                    break

        # POWERUPS
        for powerup in powerups[:]:

            powerup.update()

            if powerup.get_rect().colliderect(
                player.get_rect()
            ):

                powerup_history.append(powerup.type)

                statistics[
                    "powerups_collected"
                ] += 1

                if powerup.type == "health":

                    player.health = min(
                        player.health + 1,
                        5
                    )

                    messages.add("HEALTH RESTORED!")

                elif powerup.type == "shield":

                    player.shield = 300

                    messages.add("SHIELD ACTIVATED!")

                elif powerup.type == "rapid":

                    player.shoot_cooldown = 0

                    messages.add("RAPID FIRE!")

                powerups.remove(powerup)

            elif powerup.y > HEIGHT:

                powerups.remove(powerup)

        # PARTICLES
        for particle in particles[:]:

            particle.update()

            if particle.life <= 0:

                particles.remove(particle)

        # =====================
        # DRAW OBJECTS
        # =====================

        player.draw()

        for bullet in bullets:
            bullet.draw()

        for enemy in enemies:
            enemy.draw()

        for powerup in powerups:
            powerup.draw()

        for particle in particles:
            particle.draw()

        messages.draw()

        draw_hud()

    # =====================
    # GAME OVER
    # =====================

    else:

        draw_game_over()

    pygame.display.flip()


pygame.quit()
