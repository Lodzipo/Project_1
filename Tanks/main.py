import pygame
import os
from settings import WIDTH, HEIGHT, BLACK, player1_controls, player2_controls
from game_objects import Tank, Bullet, Obstacle
from helpers import extract_texture, generate_obstacles, show_winner

# Инициализация Pygame и создание окна
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Танковая битва")

# Загрузка атласа текстур
atlas = pygame.image.load(os.path.join(os.path.dirname(__file__), "atlas.png"))

# Извлечение текстур танков и препятствий из атласа
player1_tank_texture = extract_texture(
    atlas, 0, 0, 16, 16
)  # Текстура для первого игрока
player2_tank_texture = extract_texture(
    atlas, 16, 0, 16, 16
)  # Текстура для второго игрока
brick_texture = extract_texture(atlas, 16 * 16, 0, 16, 16)  # Текстура кирпичного блока

# Создание игровых объектов
player1 = Tank(WIDTH // 4, HEIGHT - 60, player1_controls, player1_tank_texture)
player2 = Tank(3 * WIDTH // 4, HEIGHT - 60, player2_controls, player2_tank_texture)
players = pygame.sprite.Group(player1, player2)  # Группа танков
bullets = pygame.sprite.Group()  # Группа для пуль
obstacles = pygame.sprite.Group()  # Группа для препятствий


# Основная функция запуска игры
def main():
    clock = pygame.time.Clock()  # Часы для управления FPS
    running = True  # Флаг работы игрового цикла
    generate_obstacles(
        obstacles, players, brick_texture
    )  # Генерация стартовых препятствий
    last_obstacle_update = (
        pygame.time.get_ticks()
    )  # Время последнего обновления препятствий

    while running:
        # Обработка событий пользователя
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Выход из игры
            if event.type == pygame.KEYDOWN:
                # Выстрел для первого игрока
                if event.key == player1.controls["shoot"]:
                    player1.shoot(bullets)
                # Выстрел для второго игрока
                if event.key == player2.controls["shoot"]:
                    player2.shoot(bullets)

        # Обновление состояний объектов игры
        keys = pygame.key.get_pressed()
        for tank in players:
            other_tanks = [other for other in players if other != tank]
            tank.update(keys, other_tanks, obstacles)

        bullets.update()

        # Обновление препятствий каждые 5 секунд
        now = pygame.time.get_ticks()
        if now - last_obstacle_update > 5000:
            generate_obstacles(obstacles, players, brick_texture)
            last_obstacle_update = now

        # Проверка столкновений пуль с объектами
        for bullet in bullets:
            # Столкновение пули с танком игрока 1
            if bullet.owner != player1 and pygame.sprite.collide_rect(player1, bullet):
                show_winner("Player 2", screen)
                running = False
            # Столкновение пули с танком игрока 2
            if bullet.owner != player2 and pygame.sprite.collide_rect(player2, bullet):
                show_winner("Player 1", screen)
                running = False
            # Столкновение пули с препятствиями
            for obstacle in obstacles:
                if pygame.sprite.collide_rect(bullet, obstacle):
                    bullet.kill()  # Уничтожение пули
                    obstacles.remove(obstacle)  # Удаление препятствия

        # Рендеринг всех объектов на экран
        screen.fill(BLACK)  # Заливка фона черным цветом
        players.draw(screen)  # Отрисовка всех танков
        bullets.draw(screen)  # Отрисовка всех пуль
        obstacles.draw(screen)  # Отрисовка всех препятствий
        pygame.display.flip()  # Обновление экрана

        clock.tick(60)  # Ограничение FPS до 60

    pygame.quit()  # Завершение работы игры


# Запуск игры
if __name__ == "__main__":
    main()
