import dearpygui.dearpygui as dpg

class SimulationGUI:
    def __init__(self, simulation):
        self.simulation = simulation # Ссылка на объект симуляции
        self.running = False # Флаг, указывающий, работает ли GUI

    def setup(self):
        """Настройка GUI."""
        dpg.create_context()
        # Создание окна просмотра
        dpg.create_viewport(title='Simulation', width=self.simulation.grid_width * self.simulation.grid_size + 40,
                            height=self.simulation.grid_height * self.simulation.grid_size + 115)

        with dpg.window(autosize=True, label="Map", pos=(0, 0)):
            # Добавление кнопок и текстовых элементов
            dpg.add_button(label="Reset Simulation", callback=self.simulation.reset_simulation)
            dpg.add_button(label="Drawing?", callback=self.simulation.toggle_drawing)
            dpg.add_text(default_value=f"Bots: {len(self.simulation.bots)}", tag="bot_count_text")
            dpg.add_text(default_value=f"Steps: {self.simulation.step_count}", tag="steps_count_text")
            # Создание области для отрисовки мира
            with dpg.drawlist(tag="world_drawlist", width=self.simulation.grid_width * self.simulation.grid_size,
                              height=self.simulation.grid_height * self.simulation.grid_size):
                self.draw_grid()

        dpg.set_viewport_vsync(True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.running = True

    def draw_grid(self):
        """Отрисовка сетки мира."""
        # Отрисовка белого фона
        dpg.draw_rectangle([0, 0],
                           [self.simulation.grid_width * self.simulation.grid_size, 
                            self.simulation.grid_height * self.simulation.grid_size],
                           color=[255, 255, 255, 255], fill=[255, 255, 255, 255], parent="world_drawlist")

        # Отрисовка линий сетки
        for x in range(self.simulation.grid_width):
            for y in range(self.simulation.grid_height):
                dpg.draw_rectangle([x * self.simulation.grid_size, y * self.simulation.grid_size],
                                   [(x + 1) * self.simulation.grid_size, (y + 1) * self.simulation.grid_size],
                                   color=[200, 200, 200, 255], thickness=1, parent="world_drawlist")

    def update(self):
        """Обновление GUI."""
        if self.simulation.drawing_enabled:
            # Очистка предыдущего состояния
            dpg.delete_item("world_drawlist", children_only=True)
            self.draw_grid()

            # Отрисовка ботов
            for bot in self.simulation.bots:
                x, y = bot.position
                dpg.draw_rectangle([x * self.simulation.grid_size, y * self.simulation.grid_size],
                                   [(x + 1) * self.simulation.grid_size, (y + 1) * self.simulation.grid_size],
                                   color=bot.color, fill=bot.color, parent="world_drawlist")

            # Обновление текстовой информации
            dpg.set_value("bot_count_text", f"Bots: {len(self.simulation.bots)}")
            dpg.set_value("steps_count_text", f"Steps: {self.simulation.step_count}")

        dpg.render_dearpygui_frame()

    def is_running(self):
        """Проверка, работает ли GUI."""
        return self.running and dpg.is_dearpygui_running()

    def cleanup(self):
        """Очистка GUI."""
        dpg.destroy_context()
        self.running = False