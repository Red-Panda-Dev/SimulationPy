# Модуль, описывающий класс клетки, ее функции и все что с ней связано.
import random
import numpy as np

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


class Bot:
    DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    next_bot_id = 0

    def __init__(self, color, energy, position, simulation):
        self.idx = Bot.next_bot_id
        Bot.next_bot_id += 1
        self.color = color
        self.energy = energy
        self.position = position
        self.rotation = 0
        self.brain = self.create_brain()
        self.steps = 0
        self.simulation = simulation

    def create_brain(self):
        layers = []
        num_inputs = 12
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

        return [self.energy] + inputs[:8] + [self.rotation, self.position[0], self.position[1]]

    def process_outputs(self, outputs, bots):
        max_output_index = outputs.index(max(outputs))
        if max_output_index == 0:
            self.move(bots)
        elif max_output_index == 1:
            self.rotation = (self.rotation + 1) % 8
        elif max_output_index == 2:
            self.energy += 16
        elif max_output_index == 3:
            self.multiply(bots)
        elif max_output_index == 4:
            self.attack(bots)

        self.energy -= 5

    def move(self, bots):
        dx, dy = self.DIRECTIONS[self.rotation]
        new_position = (self.position[0] + dx, self.position[1] + dy)
        if self.is_cell_free(new_position, bots):
            self.position = new_position

    def is_cell_free(self, position, bots):
        x, y = position
        if 0 <= x < self.simulation.grid_width and 0 <= y < self.simulation.grid_height:
            return not any(bot.position == position for bot in bots)
        return False

    def find_free_position(self, bots):
        return next(
            (
                (self.position[0] + dx, self.position[1] + dy)
                for dx, dy in self.DIRECTIONS
                if self.is_cell_free((self.position[0] + dx, self.position[1] + dy), bots)
            ),
            None
        )

    def multiply(self, bots):
        if self.energy < 100 or len(bots) >= self.simulation.max_bots:
            return

        child_position = self.find_free_position(bots)
        if not child_position:
            return

        child_energy = self.energy // 2
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

        new_bot = Bot(color=child_color, energy=child_energy, position=child_position, simulation=self.simulation)
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
            if self.is_similar_color(target_bot.color, self.color):
                return
            self.energy += target_bot.energy
            bots.remove(target_bot)