import pygame
import math
from settings import (
    TANK_WIDTH,
    TANK_HEIGHT,
    BULLET_SIZE,
    BLOCK_SIZE,
    TANK_SPEED,
    BULLET_SPEED,
)


# Класс танка, который управляется игроком
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, texture):
        super().__init__()
        self.original_image = pygame.transform.scale(texture, (TANK_WIDTH, TANK_HEIGHT))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = TANK_SPEED
        self.controls = controls
        self.last_shot = 0
        self.angle = 0

    def update(self, keys, other_tanks, obstacles):
        movement = [0, 0]
        if keys[self.controls["up"]]:
            movement[1] -= self.speed
            self.angle = 0
        if keys[self.controls["down"]]:
            movement[1] += self.speed
            self.angle = 180
        if keys[self.controls["left"]]:
            movement[0] -= self.speed
            self.angle = 90
        if keys[self.controls["right"]]:
            movement[0] += self.speed
            self.angle = -90

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        old_rect = self.rect.copy()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.x += movement[0]
        self.rect.y += movement[1]
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 600))

        for other_tank in other_tanks:
            if self.rect.colliderect(other_tank.rect):
                self.rect = old_rect
                break

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                self.rect = old_rect
                break

    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot > 500:
            self.last_shot = now
            rad_angle = math.radians(self.angle + 90)
            bullet_x = self.rect.centerx + math.cos(rad_angle) * (TANK_WIDTH // 2)
            bullet_y = self.rect.centery - math.sin(rad_angle) * (TANK_HEIGHT // 2)
            bullet = Bullet(bullet_x, bullet_y, self.angle + 90, self)
            bullets.add(bullet)


# Класс пули, выпускаемой танком
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, owner):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED
        self.angle = angle
        self.owner = owner
        self.velocity_x = self.speed * math.cos(math.radians(self.angle))
        self.velocity_y = self.speed * math.sin(math.radians(self.angle))

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y -= self.velocity_y
        if (
            self.rect.bottom < 0
            or self.rect.top > 600
            or self.rect.left < 0
            or self.rect.right > 800
        ):
            self.kill()


# Класс препятствий на поле
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, texture):
        super().__init__()
        self.image = pygame.transform.scale(texture, (BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
