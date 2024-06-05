import math
import pygame
import random
import time

# Initialize the game
pygame.init()
pygame.mixer.init()
pygame.font.init()
font_score = pygame.font.SysFont('Bauhaus 93', 30)
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
run = True

# Constants
BLACK = (0, 0, 0)
BULLET_SPEED = 5
BULLET_RANGE = 500
ASTEROID_SPEED = 2
SPAWN_RATE = 25  # Number of frames between spawning asteroids

# Load images
rocket_img = pygame.image.load("resources/ship.png").convert()
rocket_img = pygame.transform.scale(rocket_img, (40, 40))
rocket_img.set_colorkey(BLACK)
rocket_img = pygame.transform.rotate(rocket_img, -90)
shoot_sound = pygame.mixer.Sound("resources/bf.wav")
explo_sound = pygame.mixer.Sound("resources/explosion.wav")

ast_img1 = pygame.image.load("resources/ast1.png")
ast_img1 = pygame.transform.scale(ast_img1, (40, 40))
ast_img1.set_colorkey(BLACK)

ast_img2 = pygame.image.load("resources/ast2.png")
ast_img2 = pygame.transform.scale(ast_img2, (35, 35))
ast_img2.set_colorkey(BLACK)

ast_img3 = pygame.image.load("resources/ast3.png")
ast_img3 = pygame.transform.scale(ast_img3, (40, 40))
ast_img3.set_colorkey(BLACK)

ast_img4 = pygame.image.load("resources/ast4.png")
ast_img4 = pygame.transform.scale(ast_img4, (35, 35))
ast_img4.set_colorkey(BLACK)

ast_imgs = [ast_img1, ast_img2, ast_img3, ast_img4]

class Game_Score():
    def __init__(self):
        self.asteroids_hit = 0
        self.bullets_used = 0
        self.score = 0

    def asteroid_hit(self):
        self.asteroids_hit += 1
        self.update_score()

    def bullet_fired(self):
        self.bullets_used += 1
        self.update_score()

    def update_score(self):
        current_time = pygame.time.get_ticks()
        self.score = (self.asteroids_hit * 100) - (self.bullets_used * 2)

    def get_score(self):
        self.update_score()
        return int(self.score)

    def display_score(self, screen):
        score_text = font_score.render(f'Score: {int(self.score)}', True, (255, 255, 255))
        text_rect = score_text.get_rect()
        screen.blit(score_text,(screen.get_width() - text_rect.width - 10, screen.get_height() - text_rect.height - 10))


class Healthbar():
    def __init__(self, x, y, w, h, maxh):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = maxh

    def draw(self, screen):
        # ratio = self.hp/self.maxh
        pygame.draw.rect(screen, 'red', (self.x, self.y, self.w, self.h))
        pygame.draw.rect(screen, 'green', (self.x, self.y, self.hp, self.h))

class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = rocket_img
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(screen.get_width()//2, screen.get_height()-100))
        self.angle = 90
        self.rotation_speed = 5
        self.movement_speed = 0.1
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0, 2)
        self.deceleration = 0.95

    def update(self):
        keys = pygame.key.get_pressed()
        # if keys[pygame.K_w]:
        #     radians = math.radians(self.angle)
        #     self.velocity.x += self.movement_speed * math.cos(radians)
        #     self.velocity.y -= self.movement_speed * math.sin(radians)
        if keys[pygame.K_a]:
            #self.angle += self.rotation_speed
            self.velocity.x -= self.movement_speed
        if keys[pygame.K_d]:
            #self.angle -= self.rotation_speed
            self.velocity.x += self.movement_speed

        self.position += self.velocity
        self.velocity *= self.deceleration
        self.position.x %= screen.get_width()
        self.position.y %= screen.get_height()

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)

    def shoot(self):
        bullet_dir = pygame.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))
        bullet = Bullet(self.position, bullet_dir)
        all_sprites.add(bullet)
        bullets.add(bullet)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, direction):
        super().__init__()
        self.image = pygame.image.load("resources/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (6, 6))  # Adjust size as necessary
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(position)
        self.direction = direction
        self.distance = 0

    def update(self):
        self.position += self.direction * BULLET_SPEED
        self.distance += BULLET_SPEED
        self.rect.center = self.position
        if self.distance > BULLET_RANGE:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = random.choice(ast_imgs)
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([0, screen.get_width()])
        self.rect.y = -50
        self.direction = pygame.Vector2(random.uniform(-0.5, 0.5), 1).normalize()
        self.position = pygame.Vector2(self.rect.topleft)
        self.speed = speed

    def update(self):
        self.position += self.direction * (self.speed)
        self.rect.center = self.position
        if self.rect.top > screen.get_height() + 20 or self.rect.left < -20 or self.rect.right > screen.get_width() + 20:
            self.kill()

def spawn_asteroid():
    asteroid = Asteroid(ASTEROID_SPEED)
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

# Sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Create player
player = Rocket()
all_sprites.add(player)
health = Healthbar(20,10,100,15,100)

# Initialize game score
game_score = Game_Score()

# Main game loop
frame_count = 0
while run:
    game_score.display_score(screen)
    if health.hp <= 0:
        player.kill()
        run = False

    start = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            end = time.time()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_score.bullet_fired()
                player.shoot()
                shoot_sound.play()

    screen.fill('black')
    all_sprites.update()
    # Check for collisions between bullets and asteroids
    for bullet in bullets:
        for asteroid in asteroids:
            if asteroid.rect.collidepoint(bullet.position.x, bullet.position.y):
                game_score.asteroid_hit()
                explo_sound.play()
                bullet.kill()
                mid = time.time()
                asteroid.kill()
                ASTEROID_SPEED += 0.1

    # Check for collisions between player and asteroids
    # if pygame.sprite.spritecollideany(player, asteroids):
    #     run = False  # End the game
    #     end = time.time()
    for asteroid in asteroids :
        if player.rect.collidepoint(asteroid.position.x,asteroid.position.y):
            explo_sound.play()
            asteroid.kill()
            health.hp -= 10

    # Spawn new asteroids
    frame_count += 1
    if frame_count % SPAWN_RATE == 0:
        spawn_asteroid()

    current_score = game_score.get_score()
    all_sprites.draw(screen)
    health.draw(screen)
    pygame.display.flip()
    clock.tick(80)
pygame.quit()
