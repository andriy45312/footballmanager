import tkinter as tk
from tkinter import ttk, messagebox

class MainWindow:
    
    def __init__(self, root, controller, on_success_callback):
        self.root = root
        self.controller = controller
        self.on_success = on_success_callback 
        
        
        self.pl_purple = "#3d195b"
        self.pl_green = "#00ff85"
        
        self.root.title("Вибір команди - Premier League 2026")
        self.root.geometry("500x650")
        self.root.configure(bg=self.pl_purple)

        self.create_widgets()

    def create_widgets(self):
        
        tk.Label(
            self.root, text="ОБЕРІТЬ СВІЙ КЛУБ", bg=self.pl_purple, fg="white",
            font=("Segoe UI", 20, "bold"), pady=20
        ).pack()

        
        list_frame = tk.Frame(self.root, bg=self.pl_purple)
        list_frame.pack(fill="both", expand=True, padx=40, pady=10)

        
        self.teams_listbox = tk.Listbox(
            list_frame, font=("Segoe UI", 12), bg="white", fg=self.pl_purple,
            selectbackground=self.pl_green, selectforeground="black",
            relief="flat", bd=0, highlightthickness=0
        )
        self.teams_listbox.pack(side="left", fill="both", expand=True)

        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.teams_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.teams_listbox.config(yscrollcommand=scrollbar.set)

        
        for name in self.controller.get_all_teams_names():
            self.teams_listbox.insert(tk.END, name)

        
        tk.Button(
            self.root, text="ПОЧАТИ КАР'ЄРУ", bg=self.pl_green, fg="black",
            font=("Segoe UI", 14, "bold"), relief="flat", pady=15,
            command=self.confirm_selection, cursor="hand2"
        ).pack(fill="x", padx=40, pady=30)

    def confirm_selection(self):
        selected = self.teams_listbox.curselection()
        if not selected:
            messagebox.showwarning("Вибір", "Будь ласка, оберіть команду з переліку!")
            return

        team_name = self.teams_listbox.get(selected[0])
        
        
        if self.controller.select_team(team_name):
            
            self.controller.save_game()
            messagebox.showinfo("Успіх", f"Ласкаво просимо до клубу {team_name}!")
            
            
            self.on_success() 
        else:
            messagebox.showerror("Помилка", "Не вдалося ініціалізувати команду.")