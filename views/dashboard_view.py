import tkinter as tk
from tkinter import ttk, messagebox
from views.tactics_view import TacticsView

class DashboardView:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Football Manager 2026")
        
        self.controller = controller
        self.team = controller.current_user_team
        
        self.center_window(1050, 750)

        # --- Глобальні гарячі клавіші (Критерій 14) ---
        self.root.bind_all('<Control-s>', self.quick_save)
        self.root.bind_all('<Control-S>', self.quick_save)

        self.pl_purple, self.pl_green = "#3d195b", "#00ff85"
        self.pl_bg, self.pl_white = "#f4f4f4", "#ffffff"
        self.root.configure(bg=self.pl_bg)
        
        self.setup_language_selector()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=self.pl_bg, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", self.pl_purple)], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.team_tab = tk.Frame(self.notebook, bg=self.pl_bg)
        self.market_tab = tk.Frame(self.notebook, bg=self.pl_bg)
        self.table_tab = tk.Frame(self.notebook, bg=self.pl_bg)
        self.history_tab = tk.Frame(self.notebook, bg=self.pl_bg)

        self.notebook.add(self.team_tab, text=self.controller.t("squad"))
        self.notebook.add(self.market_tab, text=self.controller.t("market"))
        self.notebook.add(self.table_tab, text=self.controller.t("table"))
        self.notebook.add(self.history_tab, text=self.controller.t("history"))

        self.setup_team_tab()
        self.setup_market_tab()
        self.setup_table_tab()
        self.setup_history_tab()
        
        self.create_context_menu()
        self.refresh_all()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def add_button_hover(self, button, hover_color, normal_color):
        """Додає візуальну реакцію на наведення миші (Критерій 2)"""
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=normal_color))

    def quick_save(self, event=None):
        self.controller.save_game()
        messagebox.showinfo("Збереження", self.controller.t("saved"))

    def save_and_exit(self):
        """Збереження та повне закриття програми"""
        self.controller.save_game()
        self.root.destroy()

    def setup_language_selector(self):
        lang_frame = tk.Frame(self.root, bg=self.pl_bg)
        lang_frame.pack(side="top", anchor="e", padx=20, pady=5)
        
        tk.Label(lang_frame, text="🌐 Language:", bg=self.pl_bg, font=("Segoe UI", 10, "bold"), fg=self.pl_purple).pack(side="left")
        
        self.lang_cb = ttk.Combobox(lang_frame, values=["UKR", "ENG"], state="readonly", width=5)
        self.lang_cb.set(self.controller.lang)
        self.lang_cb.pack(side="left", padx=5)
        self.lang_cb.bind("<<ComboboxSelected>>", self.change_language)

    def setup_team_tab(self):
        header = tk.Frame(self.team_tab, bg=self.pl_purple, height=70)
        header.pack(fill="x")
        tk.Label(header, text=f"{self.team.name} | {self.team.stadium_name}", bg=self.pl_purple, fg="white", font=("Segoe UI", 16, "bold"), padx=20).pack(side="left")

        info_bar = tk.Frame(self.team_tab, bg=self.pl_white, pady=10)
        info_bar.pack(fill="x", padx=20, pady=10)
        self.team_budget_lbl = tk.Label(info_bar, text="", bg=self.pl_white, fg="green", font=("Segoe UI", 12, "bold"))
        self.team_budget_lbl.pack(side="left", padx=20)
        self.team_date_lbl = tk.Label(info_bar, text="", bg=self.pl_white, font=("Segoe UI", 11), fg="#555555")
        self.team_date_lbl.pack(side="right", padx=20)

        cols = ("name", "age", "pos", "rating", "fatigue", "price", "g", "a")
        self.team_tree = ttk.Treeview(self.team_tab, columns=cols, show="headings", height=15)
        headers = {"name": "ГРАВЕЦЬ", "age": "ВІК", "pos": "ПОЗ", "rating": "РЕЙТ", "fatigue": "ВТОМА", "price": "ЦІНА", "g": "⚽", "a": "👟"}
        for c in cols:
            self.team_tree.heading(c, text=headers[c], command=lambda _c=c: self.sort_column(self.team_tree, _c, False))
            self.team_tree.column(c, anchor="center", width=60)
        self.team_tree.column("name", width=200, anchor="w")

        self.team_tree.pack(fill="both", expand=True, padx=20)
        self.team_tree.bind("<Button-3>", self.show_context_menu)

        # Панель кнопок (Матч + Зберегти і вийти)
        btn_f = tk.Frame(self.team_tab, bg=self.pl_bg, pady=10)
        btn_f.pack(fill="x")
        
        self.play_btn = tk.Button(btn_f, text=self.controller.t("play"), bg=self.pl_green, font=("Segoe UI", 12, "bold"), relief="flat", padx=25, pady=10, command=self.open_tactics)
        self.play_btn.pack(side="left", padx=20)
        self.add_button_hover(self.play_btn, "#00c868", self.pl_green)

        self.exit_btn = tk.Button(btn_f, text=self.controller.t("exit_save"), bg="#e74c3c", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", padx=25, pady=10, command=self.save_and_exit)
        self.exit_btn.pack(side="left", padx=10)
        self.add_button_hover(self.exit_btn, "#c0392b", "#e74c3c")

    def setup_market_tab(self):
        top = tk.Frame(self.market_tab, bg="white", pady=15, padx=20)
        top.pack(fill="x")
        self.search_lbl = tk.Label(top, text=self.controller.t("search"), bg="white")
        self.search_lbl.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_market())
        tk.Entry(top, textvariable=self.search_var, width=30).pack(side="left", padx=10)

        cols = ("name", "pos", "rating", "price", "club")
        self.market_tree = ttk.Treeview(self.market_tab, columns=cols, show="headings")
        for c in cols:
            self.market_tree.heading(c, text=c.upper(), command=lambda _c=c: self.sort_column(self.market_tree, _c, False))
            self.market_tree.column(c, anchor="center")
        self.market_tree.pack(fill="both", expand=True, padx=20)
        
        self.buy_btn = tk.Button(self.market_tab, text=self.controller.t("buy"), bg=self.pl_purple, fg="white", font=("Segoe UI", 11, "bold"), relief="flat", pady=10, command=self.buy_player)
        self.buy_btn.pack(fill="x", padx=20, pady=15)
        self.add_button_hover(self.buy_btn, "#2a1141", self.pl_purple)

    def setup_table_tab(self):
        tk.Label(self.table_tab, text="PREMIER LEAGUE STANDINGS", bg=self.pl_bg, font=("Segoe UI", 18, "bold"), fg=self.pl_purple, pady=20).pack()
        cols = ("pos", "club", "p", "w", "d", "l", "gf", "ga", "gd", "pts")
        self.league_tree = ttk.Treeview(self.table_tab, columns=cols, show="headings", height=20)
        headers = {"pos": "№", "club": "КЛУБ", "p": "І", "w": "В", "d": "Н", "l": "П", "gf": "З", "ga": "Пр", "gd": "+/-", "pts": "ОЧКИ"}
        for c in cols:
            self.league_tree.heading(c, text=headers[c])
            self.league_tree.column(c, width=60, anchor="center")
        self.league_tree.column("club", width=200, anchor="w")
        self.league_tree.pack(fill="both", expand=True, padx=20, pady=10)

    def setup_history_tab(self):
        tk.Label(self.history_tab, text="TRANSFER HISTORY", bg=self.pl_bg, font=("Segoe UI", 18, "bold"), fg=self.pl_purple, pady=20).pack()
        cols = ("date", "player", "from", "to", "price")
        self.history_tree = ttk.Treeview(self.history_tab, columns=cols, show="headings", height=20)
        headers = {"date": "ДАТА", "player": "ГРАВЕЦЬ", "from": "ЗВІДКИ", "to": "КУДИ", "price": "ЦІНА"}
        for c in cols:
            self.history_tree.heading(c, text=headers[c])
            self.history_tree.column(c, width=100, anchor="center")
        self.history_tree.column("player", width=150, anchor="w")
        self.history_tree.pack(fill="both", expand=True, padx=20, pady=10)

    def change_language(self, event):
        self.controller.lang = self.lang_cb.get()
        self.update_ui_texts()
        self.refresh_all()

    def update_ui_texts(self):
        self.notebook.tab(0, text=self.controller.t("squad"))
        self.notebook.tab(1, text=self.controller.t("market"))
        self.notebook.tab(2, text=self.controller.t("table"))
        self.notebook.tab(3, text=self.controller.t("history"))
        
        self.play_btn.config(text=self.controller.t("play"))
        self.buy_btn.config(text=self.controller.t("buy"))
        self.exit_btn.config(text=self.controller.t("exit_save"))
        self.search_lbl.config(text=self.controller.t("search"))
        
        headers_squad = {"name": "th_player", "age": "th_age", "pos": "th_pos", "rating": "th_rating", "fatigue": "th_fatigue", "price": "th_price"}
        for col, key in headers_squad.items():
            self.team_tree.heading(col, text=self.controller.t(key))
            
        headers_market = {"name": "th_player", "pos": "th_pos", "rating": "th_rating", "price": "th_price", "club": "th_club"}
        for col, key in headers_market.items():
            self.market_tree.heading(col, text=self.controller.t(key))
            
        headers_league = {"club": "th_club", "p": "th_p", "w": "th_w", "d": "th_d", "l": "th_l", "gf": "th_gf", "ga": "th_ga", "gd": "th_gd", "pts": "th_pts"}
        for col, key in headers_league.items():
            self.league_tree.heading(col, text=self.controller.t(key))
            
        headers_hist = {"date": "th_date", "player": "th_player", "from": "th_from", "to": "th_to", "price": "th_price"}
        for col, key in headers_hist.items():
            self.history_tree.heading(col, text=self.controller.t(key))

    def refresh_all(self):
        for i in self.team_tree.get_children(): self.team_tree.delete(i)
        for p in self.team.players:
            f_display = f"-{p.fatigue}" if p.fatigue > 0 else "0"
            self.team_tree.insert("", tk.END, values=(p.name, p.age, p.position, p.rating, f_display, f"{p.price:,}", p.goals, p.assists))
        
        self.team_budget_lbl.config(text=f"{self.controller.t('budget')} {self.team.budget:,} $")
        
        date_str = self.controller.game_date.strftime('%d.%m.%Y')
        self.team_date_lbl.config(text=f"{self.controller.t('lbl_date')} {date_str} | {self.controller.t('lbl_round')} {self.controller.current_round}")

        for i in self.league_tree.get_children(): self.league_tree.delete(i)
        sorted_teams = sorted(self.controller.teams, key=lambda t: (t.points, (t.gf - t.ga), t.gf), reverse=True)
        for idx, t in enumerate(sorted_teams):
            self.league_tree.insert("", tk.END, values=(idx + 1, t.name, t.played, t.wins, t.draws, t.losses, t.gf, t.ga, (t.gf - t.ga), t.points))
        
        for i in self.history_tree.get_children(): self.history_tree.delete(i)
        for h in reversed(self.controller.transfer_history):
            self.history_tree.insert("", tk.END, values=(h['date'], h['player'], h['from'], h['to'], h['price']))
            
        self.refresh_market()

    def refresh_market(self):
        for i in self.market_tree.get_children(): self.market_tree.delete(i)
        query = self.search_var.get().lower()
        for item in self.controller.get_all_market_players():
            p = item['player']
            if query in p.name.lower():
                self.market_tree.insert("", tk.END, values=(p.name, p.position, p.rating, f"{p.price:,}", item['team_name']))

    def sort_column(self, tree, col, reverse):
        data = []
        for child in tree.get_children(''):
            val = tree.set(child, col)
            if col in ["age", "rating", "fatigue", "pts", "pos_num", "gf", "ga", "gd", "p", "w", "d", "l", "g", "a"]:
                try:
                    val = int(val.replace('-', '')) if '-' in val else int(val)
                except ValueError: val = 0
            elif col == "price":
                val = int(val.replace(',', ''))
            data.append((val, child))
        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Продати гравця", command=self.sell_player)

    def show_context_menu(self, event):
        item = self.team_tree.identify_row(event.y)
        if item:
            self.team_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def sell_player(self):
        sel = self.team_tree.selection()
        if not sel: return
        p_name = self.team_tree.item(sel[0])['values'][0]
        p_obj = next(p for p in self.team.players if p.name == p_name)
        if messagebox.askyesno("Продаж", f"Продати {p_name}?"):
            self.controller.process_sell_transaction(p_obj)
            self.refresh_all()

    def buy_player(self):
        sel = self.market_tree.selection()
        if not sel:
            messagebox.showwarning("Увага", "Будь ласка, виберіть гравця зі списку перед підписанням!")
            return
            
        p_name = self.market_tree.item(sel[0])['values'][0]
        item = next(i for i in self.controller.get_all_market_players() if i['player'].name == p_name)
        ok, msg = self.controller.process_buy_transaction(item['player'], item['team_object'])
        messagebox.showinfo("Трансфер", msg)
        self.refresh_all()

    def open_tactics(self):
        if self.controller.current_round > 38:
            self.process_season_transition()
            return
        TacticsView(self.root, self.controller, self.execute_match)

    def execute_match(self):
        res = self.controller.play_current_round()
        if res:
            res_win = tk.Toplevel(self.root)
            res_win.title(self.controller.t("match_summary"))
            res_win.geometry("500x550")
            res_win.configure(bg=self.pl_purple)
            res_win.grab_set()

            tk.Label(res_win, text=f"{self.controller.t('match_at')} {res['stadium']}", bg=self.pl_purple, fg="white", font=("Segoe UI", 10)).pack(pady=5)
            tk.Label(res_win, text=f"{res['home_team']} {res['home_score']} : {res['away_score']} {res['away_team']}", 
                     bg=self.pl_purple, fg=self.pl_green, font=("Segoe UI", 20, "bold")).pack(pady=10)
            
            goals_frame = tk.Frame(res_win, bg=self.pl_purple)
            goals_frame.pack(fill="both", expand=True, padx=20)

            h_f = tk.Frame(goals_frame, bg=self.pl_purple)
            h_f.pack(side="left", fill="both", expand=True)
            for ev in res['home_events']:
                t = f"⚽ {ev['scorer']} ({ev['assister']})" if ev['type'] == "Goal" else f"🎯 {ev['scorer']} (Pen)"
                tk.Label(h_f, text=t, fg="white", bg=self.pl_purple, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)

            a_f = tk.Frame(goals_frame, bg=self.pl_purple)
            a_f.pack(side="right", fill="both", expand=True)
            for ev in res['away_events']:
                t = f"{ev['scorer']} ({ev['assister']}) ⚽" if ev['type'] == "Goal" else f"{ev['scorer']} 🎯 (Pen)"
                tk.Label(a_f, text=t, fg="white", bg=self.pl_purple, font=("Segoe UI", 10, "bold")).pack(anchor="e", pady=2)

            if res['revenue'] > 0:
                tk.Label(res_win, text=f"{self.controller.t('stadium_rev')}: +{res['revenue']:,} $", bg=self.pl_purple, fg=self.pl_green, font=("Segoe UI", 12, "bold")).pack(pady=10)
            
            # --- ВІДМАЛЬОВКА РЕЗУЛЬТАТУ З ПЕРЕКЛАДОМ ---
            raw_result = res['result']
            res_key = "win" if raw_result == "Перемога" else "draw" if raw_result == "Нічия" else "loss"
            translated_result = self.controller.t(res_key)
            
            tk.Label(res_win, text=f"{self.controller.t('match_res')} {translated_result}", bg=self.pl_purple, fg="white", font=("Segoe UI", 12)).pack(pady=10)
            
            tk.Button(res_win, text=self.controller.t("btn_continue"), bg=self.pl_green, font=("Segoe UI", 12, "bold"), relief="flat", padx=40, pady=10, command=res_win.destroy).pack(side="bottom", pady=20)
            res_win.bind("<Return>", lambda e: res_win.destroy())
            self.refresh_all()

    def process_season_transition(self):
        if messagebox.askyesno("Кінець сезону", "38 турів зіграно! Перейти до нового сезону?"):
            self.controller.process_season_end()
            messagebox.showinfo("Новий сезон", "Гроші виплачені, календар оновлено!")
            self.refresh_all()