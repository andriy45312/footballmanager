import tkinter as tk
from tkinter import ttk, messagebox

class TransfersView(tk.Toplevel):
    def __init__(self, parent, controller, on_close_callback):
        super().__init__(parent)
        self.controller = controller
        self.on_close_callback = on_close_callback
        
        self.title("Трансферний ринок АПЛ")
        self.geometry("1000x600")
        self.transient(parent)
        self.grab_set()

        
        self.all_market_data = []
        
        self.create_widgets()

    def create_widgets(self):
        
        top_panel = ttk.Frame(self, padding=10)
        top_panel.pack(fill="x")
        
        # Бюджет
        budget = self.controller.current_user_team.budget
        self.budget_label = ttk.Label(
            top_panel, 
            text=f"Ваш бюджет: {budget:,} $", 
            font=("Arial", 12, "bold"), 
            foreground="green"
        )
        self.budget_label.pack(side="left", padx=10)

        # ПОШУК
        search_frame = ttk.Frame(top_panel)
        search_frame.pack(side="right", padx=10)
        
        ttk.Label(search_frame, text="Пошук: ").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_search) 
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side="left")

        #ТАБЛИЦЯ РИНКУ
        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill="both", expand=True)

        self.columns = ("name", "age", "pos", "rating", "price", "club")
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings")
        
        headers = {
            "name": "Гравець", "age": "Вік", "pos": "Поз.", 
            "rating": "Рейт.", "price": "Ціна $", "club": "Клуб"
        }

        for col in self.columns:
            # Додаємо сортування до кожного заголовка
            self.tree.heading(col, text=headers[col], 
                             command=lambda _col=col: self.sort_column(_col, False))
            
            # Налаштування ширини
            if col == "name": self.tree.column(col, width=180)
            elif col in ["age", "pos", "rating"]: self.tree.column(col, width=60, anchor="center")
            elif col == "price": self.tree.column(col, width=120, anchor="e")
            else: self.tree.column(col, width=140)

        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Кнопка покупки
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="КУПИТИ ГРАВЦЯ", command=self.buy_selected).pack(side="right", padx=10)
        
        # Перше завантаження даних
        self.load_initial_data()

    def load_initial_data(self):
        """Завантажує всі дані з контролера один раз"""
        self.all_market_data = self.controller.get_all_market_players()
        self.display_data(self.all_market_data)

    def display_data(self, data_list):
        """Виводить переданий список у таблицю"""
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for idx, item in enumerate(data_list):
            p = item["player"]
            self.tree.insert("", tk.END, iid=idx, values=(
                p.name, p.age, p.position, p.rating, f"{p.price:,}", item["team_name"]
            ))

    def update_search(self, *args):
        """Фільтрує список за іменем гравця"""
        search_term = self.search_var.get().lower()
        filtered_data = [
            item for item in self.all_market_data 
            if search_term in item["player"].name.lower()
        ]
        self.display_data(filtered_data)

    def sort_column(self, col, reverse):
        """Сортування колонок (враховує числа та ціни)"""
        # Отримуємо дані з таблиці
        l = []
        for child in self.tree.get_children(''):
            val = self.tree.set(child, col)
            
            # Конвертація для правильного сортування
            if col in ["age", "rating"]:
                val = int(val)
            elif col == "price":
                val = int(val.replace(',', ''))
            
            l.append((val, child))

        l.sort(reverse=reverse)

        # Переставляємо рядки
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Міняємо команду на зворотне сортування
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def buy_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Вибір", "Оберіть гравця для покупки!")
            return
            
        
        idx = int(selected[0])
        
        player_name = self.tree.item(selected[0])['values'][0]
        transaction_data = next((item for item in self.all_market_data if item["player"].name == player_name), None)

        if transaction_data:
            player = transaction_data["player"]
            seller_team = transaction_data["team_object"]
            
            success, message = self.controller.process_buy_transaction(player, seller_team)
            
            if success:
                messagebox.showinfo("Трансфер", message)
                self.on_close_callback() 
                self.destroy()           
            else:
                messagebox.showerror("Помилка", message)