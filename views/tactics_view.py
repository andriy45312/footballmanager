import tkinter as tk
from tkinter import ttk, messagebox

class TacticsView(tk.Toplevel):
    def __init__(self, parent, controller, on_play_callback):
        super().__init__(parent)
        self.controller = controller
        self.on_play_callback = on_play_callback
        
        # Використовуємо переклад для заголовка
        self.title(self.controller.t("tac_title"))
        self.geometry("600x900") 
        
        self.positions = {
            "GK": (300, 720),
            "DEF1": (100, 580), "DEF2": (230, 600), "DEF3": (370, 600), "DEF4": (500, 580),
            "MID1": (150, 400), "MID2": (300, 420), "MID3": (450, 400),
            "FWD1": (150, 180), "FWD2": (300, 150), "FWD3": (450, 180)
        }
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=600, height=800, bg="#2e7d32")
        self.canvas.pack()
        
        self.canvas.create_rectangle(10, 10, 590, 790, outline="white", width=2)
        self.canvas.create_line(10, 400, 590, 400, fill="white")

        self.slot_buttons = {}
        for pos_id, coords in self.positions.items():
            saved_player = self.controller.active_lineup.get(pos_id)
            btn_text = saved_player.name if saved_player else pos_id
            btn_bg = "#00ff85" if saved_player else "white"
            
            p_type = "".join([i for i in pos_id if not i.isdigit()])
            btn = tk.Button(self, text=btn_text, bg=btn_bg, width=12,
                           command=lambda p=pos_id, t=p_type: self.choose_player(p, t))
            self.slot_buttons[pos_id] = self.canvas.create_window(coords[0], coords[1], window=btn)

        # --- РАДІОКНОПКИ З ПЕРЕКЛАДОМ ---
        style_frame = tk.Frame(self, bg="#2e7d32")
        self.canvas.create_window(300, 30, window=style_frame)
        self.style_var = tk.StringVar(value=getattr(self.controller, 'team_style', 'Medium'))
        
        # Словник для відображення перекладених стилів
        style_labels = {
            "Defending": self.controller.t("tac_def"),
            "Medium": self.controller.t("tac_med"),
            "Attacking": self.controller.t("tac_att")
        }
        
        for s_val, s_text in style_labels.items():
            tk.Radiobutton(style_frame, text=s_text, variable=self.style_var, value=s_val, bg="#2e7d32", fg="white", selectcolor="black").pack(side="left")

        # --- ЧЕКБОКС ТА ПОВЗУНОК З ПЕРЕКЛАДОМ ---
        req_frame = tk.Frame(self)
        req_frame.pack(fill="x", padx=10, pady=5)

        self.offside_var = tk.BooleanVar(value=False)
        tk.Checkbutton(req_frame, text=self.controller.t("tac_offside"), variable=self.offside_var).pack(side="left", padx=10)

        tk.Label(req_frame, text=self.controller.t("tac_pressing")).pack(side="left", padx=(20, 5))
        self.pressing_slider = tk.Scale(req_frame, from_=0, to=100, orient="horizontal")
        self.pressing_slider.set(50)
        self.pressing_slider.pack(side="left", fill="x", expand=True)

        # --- КНОПКА З ПЕРЕКЛАДОМ ---
        tk.Button(self, text=self.controller.t("tac_confirm"), bg="yellow", font=("Arial", 12, "bold"),
                  command=self.confirm).pack(fill="x", pady=5)

    def choose_player(self, pos_id, pos_type):
        menu = tk.Menu(self, tearoff=0)
        already_on_field = [p.id for p in self.controller.active_lineup.values() if p]
        
        for p in self.controller.current_user_team.players:
            if p.position == pos_type:
                state = "disabled" if (p.id in already_on_field and self.controller.active_lineup.get(pos_id) != p) else "normal"
                menu.add_command(label=f"{p.name} (RT: {p.current_rating})", 
                                 command=lambda player=p: self.set_player(pos_id, player),
                                 state=state)
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def set_player(self, pos_id, player):
        self.controller.active_lineup[pos_id] = player
        btn_window = self.canvas.itemcget(self.slot_buttons[pos_id], 'window')
        self.nametowidget(btn_window).config(text=player.name, bg="#00ff85")

    def confirm(self):
        if len([p for p in self.controller.active_lineup.values() if p]) < 11:
            # Використовуємо переклад для помилки
            messagebox.showwarning(self.controller.t("squad").strip(), self.controller.t("tac_err"))
            return
        
        self.controller.team_style = self.style_var.get()
        self.controller.current_user_team.offside_trap = self.offside_var.get()
        self.controller.current_user_team.pressing_intensity = self.pressing_slider.get()
        
        self.on_play_callback()
        self.destroy()