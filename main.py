
import math
import pygame
import random

# Initialize the game
pygame.init()
screen = pygame.display.set_mode((650, 650), pygame.RESIZABLE)
clock = pygame.time.Clock()
run = True

# Load and scale the rocket image
rocket = pygame.image.load("resources/rocketgreen.png")
rocket = pygame.transform.scale(rocket, (int(rocket.get_width() * 0.015), int(rocket.get_height() * 0.015)))
rocket=pygame.transform.rotate(rocket,-90)
# Load asteroid image
asteroid_image = pygame.image.load("resources/asteroid.png")
asteroid_image = pygame.transform.scale(asteroid_image, (50, 50))

# Initial variables
rocket_rect = rocket.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
angle = 90  # Initial angle to make the rocket face upwards
rotation_speed = 5
movement_speed = 0.1  # Adjusted for finer control
position = pygame.Vector2(rocket_rect.center)
velocity = pygame.Vector2(0, 0)  # Initial velocity
deceleration = 0.95  # Faster deceleration factor for quicker stopping

# Bullet variables
bullets = []
bullet_speed = 5
bullet_range = 300

# Asteroid variables
asteroids = []
asteroid_speed = 2
spawn_rate = 30  # Number of frames between spawning asteroids

def spawn_asteroid():
    # Spawn asteroid at a random position on the screen
    x = random.randint(0, screen.get_width())
    y = random.randint(0, screen.get_height())
    direction = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1])).normalize()
    asteroids.append({'pos': pygame.Vector2(x, y), 'dir': direction})

# Main game loop
frame_count = 0
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Create a new bullet
                bullet_pos = pygame.Vector2(position)
                bullet_dir = pygame.Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
                bullets.append({'pos': bullet_pos, 'dir': bullet_dir, 'distance': 0})

    screen.fill('black')

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        # Calculate movement in the direction of the current angle
        radians = math.radians(angle)
        velocity.x += movement_speed * math.cos(radians)
        velocity.y -= movement_speed * math.sin(radians)

    if keys[pygame.K_a]:
        angle += rotation_speed
    if keys[pygame.K_d]:
        angle -= rotation_speed

    # Apply velocity to position
    position += velocity

    # Apply deceleration to velocity
    velocity *= deceleration

    # Ensure position stays within screen bounds
    position.x %= screen.get_width()
    position.y %= screen.get_height()

    # Rotate the rocket image
    rotated_rocket = pygame.transform.rotate(rocket, angle)
    rotated_rect = rotated_rocket.get_rect(center=(position.x, position.y))

    # Draw the rotated rocket
    screen.blit(rotated_rocket, rotated_rect.topleft)

    # Update and draw bullets
    for bullet in bullets[:]:
        bullet['pos'] += bullet['dir'] * bullet_speed
        bullet['distance'] += bullet_speed
        if bullet['distance'] > bullet_range:
            bullets.remove(bullet)
        else:
            pygame.draw.circle(screen, 'red', (int(bullet['pos'].x), int(bullet['pos'].y)), 3)

    # Spawn new asteroids
    frame_count += 1
    if frame_count % spawn_rate == 0:
        spawn_asteroid()

    # Update and draw asteroids
    for asteroid in asteroids[:]:
        asteroid['pos'] += asteroid['dir'] * asteroid_speed
        # Check for collision with rocket
        if rotated_rect.collidepoint(asteroid['pos'].x, asteroid['pos'].y):
            run = False  # End the game
        # Draw the asteroid
        asteroid_rect = asteroid_image.get_rect(center=asteroid['pos'])
        screen.blit(asteroid_image, asteroid_rect.topleft)

    # Check for bullet-asteroid collisions
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            asteroid_rect = asteroid_image.get_rect(center=asteroid['pos'])
            if asteroid_rect.collidepoint(bullet['pos'].x, bullet['pos'].y):
                bullets.remove(bullet)
                asteroids.remove(asteroid)
                break

    pygame.display.flip()
    clock.tick(60)

pygame.quit()




