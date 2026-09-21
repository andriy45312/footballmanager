import tkinter as tk
from controllers.main_controller import MainController
from views.start_screen import StartScreen
from views.main_window import MainWindow
from views.dashboard_view import DashboardView

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.controller = MainController()
        self.show_start_screen()

    def show_start_screen(self):
        # Очищуємо вікно перед малюванням
        for widget in self.root.winfo_children():
            widget.destroy()
        StartScreen(self.root, self.controller, self.handle_slot_selection)

    def handle_slot_selection(self, slot):
     
        self.controller.current_slot = slot
        if self.controller.load_game(slot):
            # Якщо сейв знайшли — йдемо в гру
            self.show_dashboard()
        else:
            # Якщо сейва нема — завантажуємо дані з JSON і відкриваємо вибір команди
            if self.controller.load_data():
                self.show_team_selection()

    def show_team_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Викликаємо твоє вікно вибору команди
        MainWindow(self.root, self.controller, self.show_dashboard)

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.dashboard = DashboardView(self.root, self.controller)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()