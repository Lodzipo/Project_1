import pygame
import random
from settings import BLOCK_SIZE
from game_objects import Obstacle


# Функция для извлечения текстуры из атласа
def extract_texture(atlas, x, y, width, height):
    texture = pygame.Surface((width, height), pygame.SRCALPHA)
    texture.blit(atlas, (0, 0), (x, y, width, height))
    return texture


# Генерация случайных препятствий на поле
def generate_obstacles(obstacles, players, brick_texture):
    obstacles.empty()
    occupied_positions = [tank.rect.topleft for tank in players]
    for _ in range(10):
        while True:
            x = random.randint(0, 800 // BLOCK_SIZE - 1) * BLOCK_SIZE
            y = random.randint(0, 600 // BLOCK_SIZE - 1) * BLOCK_SIZE
            if (x, y) not in occupied_positions:
                break
        obstacle = Obstacle(x, y, brick_texture)
        obstacles.add(obstacle)


# Отображение сообщения о победителе
def show_winner(winner, screen):
    font = pygame.font.Font(None, 74)
    text = font.render(f"{winner} Wins!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(400, 300))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)
