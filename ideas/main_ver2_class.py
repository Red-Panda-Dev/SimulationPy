import numpy as np
import random
import dearpygui.dearpygui as dpg
from time import sleep
import threading
# Основной класс симуляции
class Simulation:
    def __init__(self, grid_width=80, grid_height=80, grid_size=6, max_bots=200):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid_size = grid_size
        self.max_bots = max_bots
        self.bots = []
        self.running = False
        self.step_count = 0
        self.update_needed = True
        self.drawing_enabled = True
        self.lock = threading.Lock()  # Блокировка для потокобезопасности

    def start(self):
        self.reset_simulation()
        self.running = True
        threading.Thread(target=self.simulation_thread, daemon=True).start()

    def stop(self):
        self.running = False

    def simulation_thread(self):
        while self.running:
            with self.lock:  # Защита доступа к общим данным
                self.update_simulation()
                self.update_needed = True  # Устанавливаем флаг обновления интерфейса
                #sleep(0.01)  # Задержка для снижения загрузки процессора

    def reset_simulation(self):
        self.step_count = 0
        self.bots = [Bot(color=[random.randint(0, 255) for _ in range(3)], energy=100,
                         position=(random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))) for i in range(100)]

    def update_simulation(self):
        # Удаляем ботов с низкой энергией
        self.bots = [bot for bot in self.bots if bot.energy > 0]

        # Функция для обновления группы ботов
        def update_group(start, end):
            for bot in self.bots[start:end]:
                bot.steps += 1  # Увеличиваем счетчик шагов
                if bot.steps >= 25:
                    bot.energy = 0  # Умираем, если достигли 25 шагов
                else:
                    bot.act(self.bots)

        # Определяем количество потоков
        num_threads = 4  # Например, 4 потока
        threads = []
        group_size = len(self.bots) // num_threads

        # Запускаем потоки
        for i in range(num_threads):
            start_index = i * group_size
            # Обрабатываем последний поток отдельно, чтобы захватить всех ботов
            end_index = (i + 1) * group_size if i < num_threads - 1 else len(self.bots)
            thread = threading.Thread(target=update_group, args=(start_index, end_index))
            threads.append(thread)
            thread.start()

        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()

        '''# Обновляем ботов
        for bot in self.bots:
            bot.act(self.bots)'''

        self.step_count += 1  # Увеличиваем количество шагов на 1
        dpg.set_value("bot_count_text", f"Bots: {len(self.bots)}")
        dpg.set_value("steps_count_text", f"Steps: {self.step_count}")

    def toggle_drawing(self):
        self.drawing_enabled = not self.drawing_enabled


# Класс для нейрона
class Neuron:
    def __init__(self, neuron_type='normal', bias=0.0, num_inputs=12):
        self.neuron_type = neuron_type
        self.bias = bias
        self.weights = np.random.uniform(-1, 1, num_inputs)

    def activate(self, inputs):
        x = np.dot(self.weights, inputs) + self.bias
        if self.neuron_type == 'normal':
            return self.step_function(x)
        elif self.neuron_type == 'radial':
            return self.radial_basis_function(x)
        elif self.neuron_type == 'random':
            return self.random_neuron_activation(x, self.bias)

    @staticmethod
    def step_function(x):
        return 1 if x >= 0.5 else 0

    @staticmethod
    def radial_basis_function(x):
        return 1 if 0.45 <= x <= 0.55 else 0

    @staticmethod
    def random_neuron_activation(x, bias):
        return 1 if x >= random.random() + bias else 0


# Класс для бота
class Bot:
    DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    # Статическая переменная для отслеживания следующего ID бота
    next_bot_id = 0
    def __init__(self, color, energy, position):
        self.idx = Bot.next_bot_id  # Присваиваем текущий ID
        Bot.next_bot_id += 1  # Увеличиваем следующий ID
        self.color = color
        self.energy = energy
        self.position = position
        self.rotation = 0  # направление взгляда
        self.brain = self.create_brain()
        self.steps = 0  # Добавляем переменную для отслеживания шагов

    def create_brain(self):
        layers = []
        num_inputs = 12  # начальное количество входов соответствует количеству сенсоров
        for _ in range(num_inputs):
            layer = [Neuron(neuron_type=random.choice(['normal', 'radial', 'random']),
                            bias=random.uniform(-1, 1), num_inputs=num_inputs)
                     for _ in range(12)]
            layers.append(layer)
        return layers

    def think(self, inputs):
        outputs = inputs
        for layer in self.brain:
            outputs = [neuron.activate(outputs) for neuron in layer]
        return outputs

    def act(self, bots):
        inputs = self.sense(bots)
        outputs = self.think(inputs)
        self.process_outputs(outputs, bots)

    def sense(self, bots):
        inputs = []
        for dx, dy in self.DIRECTIONS:
            neighbor_position = (self.position[0] + dx, self.position[1] + dy)
            neighbor_bot = next((b for b in bots if b.position == neighbor_position), None)
            inputs.append(1 if neighbor_bot else 0)

        return [self.energy] + inputs[:8] + [self.rotation, self.position[1], self.position[1]]

    def process_outputs(self, outputs, bots):
        max_output_index = outputs.index(max(outputs))
        if max_output_index == 0:   # move
            self.move(bots)
        elif max_output_index == 1:  # rotate
            self.rotation = (self.rotation + 1) % 8
        elif max_output_index == 2:  # photosynth
            self.energy += 16
        elif max_output_index == 3:  # multiply
            self.multiply(bots)
        elif max_output_index == 4:  # attack
            self.attack(bots)

        self.energy -= 5

    def move(self, bots):
        dx, dy = self.DIRECTIONS[self.rotation]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        if self.is_cell_free(new_position, bots):
            self.position = new_position

    @staticmethod
    def is_cell_free(position, bots):
        x, y = position
        if 0 <= x < simulation.grid_width and 0 <= y < simulation.grid_height:
            return not any(bot.position == position for bot in bots)
        return False

    def find_free_position(self, bots):
        # Ищем свободную клетку вокруг текущей позиции
        return next(
            (
                (self.position[0] + dx, self.position[1] + dy)
                for dx, dy in self.DIRECTIONS
                if self.is_cell_free((self.position[0] + dx, self.position[1] + dy), bots)
            ),
            None
        )


    def multiply(self, bots):
        if self.energy < 100 or len(bots) >= simulation.max_bots:
            return

        child_position = self.find_free_position(bots)
        if not child_position:
            return

        child_energy = self.energy // 2
        #self.energy -= child_energy
        child_brain = [list(layer) for layer in self.brain]

        if random.randint(1, 5) == 1:
            for _ in range(random.randint(1, 5)):
                layer_idx = random.randint(0, len(child_brain) - 1)
                neuron_idx = random.randint(0, len(child_brain[layer_idx]) - 1)
                child_brain[layer_idx][neuron_idx] = Neuron(
                    neuron_type=random.choice(['normal', 'radial', 'random']),
                    bias=random.uniform(-1, 1),
                    num_inputs=12
                )
            child_color = [min(max(c + random.randint(-10, 10), 0), 255) for c in self.color]
        else:
            child_color = self.color.copy()

        new_bot = Bot(color=child_color, energy=child_energy, position=child_position)
        new_bot.brain = child_brain
        bots.append(new_bot)

    @staticmethod
    def is_similar_color(color1, color2, tolerance=15):
        return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

    def attack(self, bots):
        dx, dy = self.DIRECTIONS[self.rotation]
        target_position = (self.position[0] + dx, self.position[1] + dy)
        target_bot = next((b for b in bots if b.position == target_position), None)

        if target_bot:
            # Проверяем, является ли цель своим собратом (если у вас есть способ идентифицировать)
            # Например, если у ботов есть одинаковые цвета или другой идентификатор
            if self.is_similar_color(target_bot.color, self.color):
                return  # Не атакуем, если это свой бот
            self.energy += target_bot.energy
            bots.remove(target_bot)


# Настройка интерфейса DearPyGui
simulation = Simulation()

dpg.create_context()
dpg.create_viewport(title='Simulation', width=simulation.grid_width * simulation.grid_size + 40,
                    height=simulation.grid_height * simulation.grid_size + 115)

def draw_grid():
    dpg.draw_rectangle([0, 0],
                       [simulation.grid_width * simulation.grid_size, simulation.grid_height * simulation.grid_size],
                       color=[255, 255, 255, 255], fill=[255, 255, 255, 255], parent="world_drawlist")
    for x in range(simulation.grid_width):
        for y in range(simulation.grid_height):
            dpg.draw_rectangle([x * simulation.grid_size, y * simulation.grid_size],
                               [(x + 1) * simulation.grid_size, (y + 1) * simulation.grid_size],
                               color=[200, 200, 200, 255], thickness=1, parent="world_drawlist")


with dpg.window(autosize=True, label="Map", pos=(0, 0)):
    dpg.add_button(label="Reset Simulation", callback=simulation.reset_simulation)
    dpg.add_button(label="Drawing?", callback=simulation.toggle_drawing)
    bot_count_text = dpg.add_text(default_value=f"Bots: {len(simulation.bots)}", tag="bot_count_text")
    steps = dpg.add_text(default_value=f"Steps: {simulation.step_count}", tag="steps_count_text")
    with dpg.drawlist(tag="world_drawlist", width=simulation.grid_width * simulation.grid_size, height=simulation.grid_height * simulation.grid_size):
        draw_grid()

dpg.set_viewport_vsync(True)
dpg.setup_dearpygui()
dpg.show_viewport()

# Запуск симуляции
simulation.start()

while dpg.is_dearpygui_running():
    if simulation.update_needed and simulation.drawing_enabled:
        # Очистить текущие рисунки
        dpg.delete_item("world_drawlist", children_only=True)
        # Рисуем сетку
        draw_grid()

        for bot in simulation.bots:
            x, y = bot.position
            dpg.draw_rectangle([x * simulation.grid_size, y * simulation.grid_size],
                               [(x + 1) * simulation.grid_size, (y + 1) * simulation.grid_size],
                               color=bot.color, fill=bot.color, parent="world_drawlist")

        dpg.set_value(bot_count_text, f"Bots: {len(simulation.bots)}")
        dpg.set_value(steps, f"Steps: {simulation.step_count}")

        simulation.update_needed = False  # Сбрасываем флаг обновления интерфейса

    dpg.render_dearpygui_frame()

dpg.destroy_context()
