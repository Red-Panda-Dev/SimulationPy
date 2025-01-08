import numpy as np
import random, time, concurrent.futures

# Определяем функции активации
def step_function(x):
    return 1 if x >= 0.5 else 0

def radial_basis_function(x):
    return 1 if 0.45 <= x <= 0.55 else 0

def random_neuron_activation(x, bias):
    return 1 if x >= random.random() + bias else 0

# Класс для нейрона
class Neuron:
    def __init__(self, neuron_type='normal', bias=0.0, num_inputs=5):
        self.neuron_type = neuron_type
        self.bias = bias
        self.weights = np.random.uniform(-1, 1, num_inputs)

    def activate(self, inputs):
        x = np.dot(self.weights, inputs) + self.bias
        if self.neuron_type == 'normal':
            return step_function(x)
        elif self.neuron_type == 'radial':
            return radial_basis_function(x)
        elif self.neuron_type == 'random':
            return random_neuron_activation(x, self.bias)

# Класс для бота
class Bot:
    DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    def __init__(self, color, energy, position):
        self.color = color
        self.energy = energy
        self.position = position
        self.rotation = 0  # направление взгляда
        self.brain = self.create_brain()

    def create_brain(self):
        layers = []
        num_inputs = 5  # начальное количество входов соответствует количеству сенсоров
        for _ in range(6):
            layer = [Neuron(neuron_type=random.choice(['normal', 'radial', 'random']),
                            bias=random.uniform(-1, 1), num_inputs=num_inputs)
                     for _ in range(5)]
            layers.append(layer)
            num_inputs = 5  # количество нейронов в каждом следующем слое
        return layers

    def think(self, inputs):
        outputs = inputs
        for layer in self.brain:
            outputs = [neuron.activate(outputs) for neuron in layer]
        return outputs

    def act(self, world):
        # Получаем входные данные (пример)
        inputs = self.sense(world)
        # Обрабатываем их через мозг
        outputs = self.think(inputs)
        # Реализуем действия на основе выходных сигналов
        self.process_outputs(outputs)

    def sense(self, world):
        # Определяем смещение для направления взгляда
        dx, dy = self.DIRECTIONS[self.rotation]
        x, y = self.position
        nx, ny = x + dx, y + dy

        # Проверяем границы мира и что находится перед ботом
        if 0 <= nx < world.shape[0] and 0 <= ny < world.shape[1]:
            cell_content = world[nx, ny]
        else:
            cell_content = -1  # например, -1 для обозначения стены или пустого пространства

        # Пример получения входных данных
        return [self.energy, cell_content, 0, self.rotation, self.position[1]]

    def process_outputs(self, outputs):
        # Пример обработки выходных данных
        if outputs[0]:  # rotate
            self.rotation = (self.rotation + 1) % 8
        if outputs[1]:  # move
            self.move()
        if outputs[2]:  # photosynth
            self.energy += 1
        if outputs[3]:  # multiply
            self.multiply()
        if outputs[4]:  # attack
            self.attack()

    def move(self):
        dx, dy = self.DIRECTIONS[self.rotation]
        self.position = (self.position[0] + dx, self.position[1] + dy)

    def multiply(self):
        # Пример размножения
        pass

    def attack(self):
        # Пример атаки
        pass

# Пример создания мира и ботов
world = np.zeros((100, 100))  # 100x100 клеток
bots = [Bot(color=random.randint(0, 255), energy=100, position=(random.randint(0, 100), random.randint(0, 100))) for _ in range(1000)]

# Функция для обработки одного бота
def process_bot(bot, world):
    bot.act(world)
    #return f"Position: {bot.position}, Energy: {bot.energy}"

# Запуск симуляции
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
    for _ in range(10000):  # 10000 шагов
        futures = [executor.submit(process_bot, bot, world) for bot in bots]
        for future in concurrent.futures.as_completed(futures):
            pass
            #print(future.result())

end_time = time.time()
print(f"Simulation completed in {end_time - start_time:.2f} seconds")