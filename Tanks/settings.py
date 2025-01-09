import pygame

# Основные параметры игрового окна
WIDTH, HEIGHT = 800, 600  # Размер окна
BLACK = (0, 0, 0)  # Цвет фона

# Размеры игровых объектов
TANK_WIDTH, TANK_HEIGHT = 40, 40  # Размер танков
BULLET_SIZE = 10  # Размер пуль
BLOCK_SIZE = 40  # Размер блока препятствия

# Скорость движения объектов
TANK_SPEED = 5  # Скорость движения танка
BULLET_SPEED = 10  # Скорость движения пули

# Управление для игроков
player1_controls = {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "shoot": pygame.K_SPACE,
}
player2_controls = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "shoot": pygame.K_RETURN,
}
