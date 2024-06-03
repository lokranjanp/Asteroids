import math
import pygame
import random

# Initialize the game
pygame.init()
pygame.mixer.init(441)
screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
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

class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = rocket_img
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        self.angle = 90
        self.rotation_speed = 5
        self.movement_speed = 0.1
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0, 2)
        self.deceleration = 0.95

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            radians = math.radians(self.angle)
            self.velocity.x += self.movement_speed * math.cos(radians)
            self.velocity.y -= self.movement_speed * math.sin(radians)
        if keys[pygame.K_a]:
            self.angle += self.rotation_speed
        if keys[pygame.K_d]:
            self.angle -= self.rotation_speed

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
    def __init__(self):
        super().__init__()
        self.image = random.choice(ast_imgs)
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([0, screen.get_width()])
        self.rect.y = random.randint(0, screen.get_height())
        self.direction = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()
        self.position = pygame.Vector2(self.rect.center)

    def update(self):
        self.position += self.direction * ASTEROID_SPEED
        self.rect.center = self.position
        if self.rect.top > screen.get_height() + 20 or self.rect.left < -20 or self.rect.right > screen.get_width() + 20:
            self.kill()

def spawn_asteroid():
    asteroid = Asteroid()
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

# Sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Create player
player = Rocket()
all_sprites.add(player)

# Main game loop
frame_count = 0
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
                shoot_sound.play()

    screen.fill('black')

    all_sprites.update()

    # Check for collisions between bullets and asteroids
    for bullet in bullets:
        for asteroid in asteroids:
            if asteroid.rect.collidepoint(bullet.position.x, bullet.position.y):
                explo_sound.play()
                bullet.kill()
                asteroid.kill()

    # Check for collisions between player and asteroids
    if pygame.sprite.spritecollideany(player, asteroids):
        run = False  # End the game

    # Spawn new asteroids
    frame_count += 1
    if frame_count % SPAWN_RATE == 0:
        spawn_asteroid()

    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
