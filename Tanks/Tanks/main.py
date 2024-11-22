import pygame
from pygame.locals import *
from game import Game  # Импортируем класс Game, который отвечает за логику игры
from config import *  # Импортируем настройки игры (например, размеры экрана)
from util import Direction  # Импортируем класс Direction для управления направлениями танка

if __name__ == '__main__':
    pygame.init()  # Инициализация Pygame
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))  # Создание окна с заданными размерами

    clock = pygame.time.Clock()  # Создаем объект Clock для контроля частоты кадров

    game = Game()  # Создаем объект игры

    running = True  # Флаг для управления циклом игры
    while running:  # Основной цикл игры
        for event in pygame.event.get():  # Обработка событий
            if event.type == QUIT:  # Если событие - выход
                running = False  # Выход из цикла

            elif event.type == KEYDOWN:  # Если нажата клавиша
                if event.key == K_t:  # Если нажата клавиша 'T'
                    game.switch_my_tank()  # Переключаем танк игрока
                elif event.key == K_ESCAPE:  # Если нажата клавиша 'ESC'
                    running = False  # Выход из цикла
                elif event.key == K_SPACE:  # Если нажата 'SPACE'
                    game.fire()  # Игрок стреляет
                elif event.key == K_r:  # Если нажата 'R'
                    game = Game()  # Перезапускаем игру
                elif event.key == K_p:  # Если нажата 'P'
                    game.testus()  # Запускаем тестовую функцию

        keys = pygame.key.get_pressed()  # Получаем текущее состояние всех клавиш

        # Определяем направление движения танка в зависимости от нажатых клавиш
        if keys[pygame.K_UP] or keys[pygame.K_w]:  # Если кнопка ВВЕРХ или 'W' нажата
            game.my_tank_move_to_direction = Direction.UP  # Устанавливаем направление ВВЕРХ
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:  # Если кнопка ВНИЗ или 'S' нажата
            game.my_tank_move_to_direction = Direction.DOWN  # Устанавливаем направление ВНИЗ
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:  # Если кнопка НАЛЕВО или 'A' нажата
            game.my_tank_move_to_direction = Direction.LEFT  # Устанавливаем направление НАЛЕВО
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Если кнопка НАПРАВО или 'D' нажата
            game.my_tank_move_to_direction = Direction.RIGHT  # Устанавливаем направление НАПРАВО
        else:
            game.my_tank_move_to_direction = None  # Если ни одна кнопка не нажата, сбрасываем направление

        screen.fill((128, 128, 128))  # Заполняем экран серым цветом

        game.update()  # Обновляем состояние игры
        game.render(screen)  # Отрисовываем текущий кадр игры на экране

        if DEBUG:  # Если режим отладки включен
            pygame.draw.circle(screen, (0, 255, 255), game.my_tank.gun_point, 4,
                               1)  # Рисуем кружок вокруг точки стрельбы танка

        pygame.display.flip()  # Обновляем экран

        clock.tick(30)  # Ограничиваем частоту кадров до 30 FPS

    pygame.quit()  # Завершаем работу Pygame при выходе из цикла