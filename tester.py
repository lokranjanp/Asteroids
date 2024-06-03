import pygame
import random
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound

# Constants
WIDTH = 400
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Window")
clock = pygame.time.Clock()

# Paths
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "shooter-graphics")
song_folder = os.path.join(game_folder, "sounds")

# Load images
background = pygame.image.load(os.path.join(img_folder, "back.png")).convert()
background_rect = background.get_rect()
ship_img = pygame.image.load(os.path.join(img_folder, "ship.png")).convert()
ship_tag = pygame.transform.scale(ship_img, (15, 15))
ship_tag.set_colorkey(BLACK)
laser_img = pygame.image.load(os.path.join(img_folder, "ebullet1.png")).convert()

# Load asteroid images
asteroid_images = []
asteroid_list = ["ast1.png", "ast2.png", "ast3.png", "ast4.png"]
for img in asteroid_list:
    asteroid_images.append(pygame.image.load(os.path.join(img_folder, img)).convert())

# Load powerup images
power_img = {
    'gun': pygame.image.load(os.path.join(img_folder, 'bolt_gold.png')).convert(),
    'health': pygame.image.load(os.path.join(img_folder, 'pill_green.png')).convert(),
    'live': pygame.image.load(os.path.join(img_folder, 'powerupRed_star.png')).convert()
}

# Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join(song_folder, "bf.wav"))
explo_sound = pygame.mixer.Sound(os.path.join(song_folder, 'explosion.wav'))
background_sound = pygame.mixer.music.load(os.path.join(song_folder, 'bck.wav'))
power_sound = pygame.mixer.Sound(os.path.join(song_folder, "sfx_zap.ogg"))
player_die_sound = pygame.mixer.Sound(os.path.join(song_folder, 'shipdes.ogg'))

# Explosion animations
explosion_anim = {'lar': [], 'sml': [], 'player': []}
for i in range(9):
    filename = 'regularExplosion0' + str(i) + '.png'
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lr = pygame.transform.scale(img, (60, 60))
    img_sm = pygame.transform.scale(img, (30, 30))
    explosion_anim['lar'].append(img_lr)
    explosion_anim['sml'].append(img_sm)
    filename = 'sonicExplosion0' + str(i) + '.png'
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_tr = pygame.transform.scale(img, (100, 100))
    explosion_anim['player'].append(img_tr)

# Define classes
class Battleship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.transform.scale(ship_img, (60, 60))
        self.original_image.set_colorkey(BLACK)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.radius = 29
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.angle = 90
        self.rotation_speed = 5
        self.movement_speed = 0.1
        self.position = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(0, 2)
        self.deceleration = 0.95
        self.health = 100
        self.lives = 2
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power_level = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        if self.power_level >= 2 and pygame.time.get_ticks() - self.power_timer > 3000:
            self.power_level -= 1
            self.power_timer = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.move_forward()
        if keys[pygame.K_a]:
            self.rotate_left()
        if keys[pygame.K_d]:
            self.rotate_right()

        self.position += self.velocity
        self.velocity *= self.deceleration
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)

    def move_forward(self):
        radians = math.radians(self.angle)
        self.velocity.x += self.movement_speed * math.cos(radians)
        self.velocity.y -= self.movement_speed * math.sin(radians)

    def rotate_left(self):
        self.angle += self.rotation_speed

    def rotate_right(self):
        self.angle -= self.rotation_speed

    def shoot(self):
        if self.power_level == 1:
            bullet = Bullet(self.rect.centerx, self.rect.top, self.angle)
            all_sprites.add(bullet)
            Bull.add(bullet)
            shoot_sound.play()
        elif self.power_level >= 2:
            bullet1 = Bullet(self.rect.centerx - 25, self.rect.top - 20, self.angle)
            bullet2 = Bullet(self.rect.centerx + 25, self.rect.top - 20, self.angle)
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            Bull.add(bullet1)
            Bull.add(bullet2)
            shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def powerup(self):
        self.power_level += 1
        self.power_timer = pygame.time.get_ticks()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(laser_img, (5, 10))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = 10
        self.angle = angle

    def update(self):
        radians = math.radians(self.angle)
        self.rect.x += self.speed * math.cos(radians)
        self.rect.y -= self.speed * math.sin(radians)
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > WIDTH or self.rect.top > HEIGHT:
            self.kill()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = pygame.transform.scale(random.choice(asteroid_images), (30, 30))
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = 15
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-140, -40)
        self.speedy = random.randrange(1, 6)
        self.speedx = -2 + random.randrange(0, 4)
        self.rot = 0
        self.rotspeed = random.randrange(-10, 10)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 60:
            self.last_update = now
            self.rot = (self.rot + self.rotspeed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 20 or self.rect.left < -20 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-140, -40)
            self.speedy = random.randrange(1, 7)


class Explo(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['gun', 'health', 'live'])
        self.image = power_img[self.type]
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


def create_new_mobs():
    for i in range(6):
        new_mob = Mob()
        all_sprites.add(new_mob)
        mobs.add(new_mob)


# Sprite groups
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
Bull = pygame.sprite.Group()
powers = pygame.sprite.Group()

player = Battleship()
all_sprites.add(player)
create_new_mobs()

score = 0
pygame.mixer.music.play(loops=-1)

# Main loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    hits = pygame.sprite.groupcollide(mobs, Bull, True, True)
    for hit in hits:
        score += 50 - hit.radius
        explo_sound.play()
        expl = Explo(hit.rect.center, 'lar')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_mob = Mob()
        all_sprites.add(new_mob)
        mobs.add(new_mob)

    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()
        if hit.type == 'health':
            player.health += random.randrange(10, 30)
            if player.health >= 100:
                player.health = 100
        if hit.type == 'live':
            player.lives += 1
            if player.lives >= 5:
                player.lives = 5

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.health -= hit.radius * 2
        expl = Explo(hit.rect.center, 'sml')
        all_sprites.add(expl)
        new_mob = Mob()
        all_sprites.add(new_mob)
        mobs.add(new_mob)
        if player.health <= 0:
            player_die_sound.play()
            death_explosion = Explo(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.health = 100

    if player.lives == 0 and not death_explosion.alive():
        running = False

    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
