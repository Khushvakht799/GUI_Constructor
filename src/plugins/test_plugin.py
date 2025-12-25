class Plugin:
    def name(self):
        return "Тестовый плагин"

    def run(self, gui):
        gui.log("Запущен тестовый плагин")