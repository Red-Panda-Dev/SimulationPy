import multiprocessing
from multiprocessing import Queue

import random, time
from gui import SimulationGUI
from cell import Bot


class Simulation:
    def __init__(self, grid_width=100, grid_height=100, grid_size=6, max_bots=2000):
        """
        Инициализация симуляции с заданными параметрами.
        """
        self.grid_width = grid_width # Ширина сетки мира
        self.grid_height = grid_height # Высота сетки мира
        self.grid_size = grid_size # Размер одной клетки сетки в пикселях
        self.max_bots = max_bots # Максимальное количество ботов
        self.bots = [] # Список всех ботов в симуляции
        self.step_count = 0 # Счетчик шагов симуляции
        self.running = False # Флаг, указывающий, запущена ли симуляция
        self.drawing_enabled = True # Флаг, указывающий, нужно ли обновлять отрисовку
        self.reset_simulation() # Инициализация начального состояния симуляции

    def start(self):
        """Запуск симуляции."""
        self.running = True

    def stop(self):
        """Остановка симуляции."""
        self.running = False


    def reset_simulation(self):
        """Сброс симуляции к начальному состоянию."""
        self.bots = [
            Bot(
                color=[random.randint(0, 255) for _ in range(3)], # Случайный цвет
                energy=100, # Начальная энергия
                position=(
                    random.randint(0, self.grid_width - 1),
                    random.randint(0, self.grid_height - 1)
                ), # Случайная позиция
                simulation=self
            ) for _ in range(100) # Создаем 100 ботов
        ]
        self.step_count = 0 # Сброс счетчика шагов

    def update_simulation(self):
        """Обновление состояния симуляции на один шаг."""
        if not self.running:
            return

        self.step_count += 1  # Увеличение счетчика шагов
        for bot in self.bots[:]: # Итерация по копии списка ботов
            bot.act(self.bots) # Выполнение действия бота
            if bot.energy <= 0:
                self.bots.remove(bot) # Удаление бота, если его энергия закончилась

    def toggle_drawing(self):
        """Переключение режима отрисовки."""
        self.drawing_enabled = not self.drawing_enabled


if __name__ == "__main__":
    simulation = Simulation() # Создание объекта симуляции
    gui = SimulationGUI(simulation) # Создание объекта GUI
    gui.setup() # Настройка GUI
    simulation.start() # Запуск симуляции

    # Основной цикл программы
    while gui.is_running():
        simulation.update_simulation() # Обновление состояния симуляции
        gui.update() # Обновление GUI

    gui.cleanup() # Очистка ресурсов GUI при завершении программы