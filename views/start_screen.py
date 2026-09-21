import tkinter as tk
from tkinter import ttk, messagebox
import os

class StartScreen:
    def __init__(self, root, controller, on_slot_selected):
        self.root = root
        self.controller = controller
        self.on_slot_selected = on_slot_selected
        
        self.pl_purple, self.pl_green = "#3d195b", "#00ff85"
        self.root.title(self.controller.t("start_title"))
        self.root.geometry("450x650") 
        self.root.configure(bg=self.pl_purple)

        
        self.setup_language_selector()

        # Заголовок
        self.title_lbl = tk.Label(
            self.root, text="PREMIER LEAGUE", fg=self.pl_green, bg=self.pl_purple, 
            font=("Segoe UI", 26, "bold"), pady=20
        )
        self.title_lbl.pack()

        # Контекстне меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label=self.controller.t("del_save"), command=self.confirm_delete)
        
        self.selected_slot_to_delete = None
        self.slot_buttons = {}

        self.buttons_frame = tk.Frame(self.root, bg=self.pl_purple)
        self.buttons_frame.pack(fill="both", expand=True)

        for i in range(1, 6):
            self.create_slot_button(i)

    def setup_language_selector(self):
        lang_frame = tk.Frame(self.root, bg=self.pl_purple)
        lang_frame.pack(side="top", anchor="e", padx=20, pady=10)
        
        self.lang_lbl = tk.Label(lang_frame, text="🌐 Language:", bg=self.pl_purple, font=("Segoe UI", 10, "bold"), fg="white")
        self.lang_lbl.pack(side="left")
        
        self.lang_cb = ttk.Combobox(lang_frame, values=["UKR", "ENG"], state="readonly", width=5)
        self.lang_cb.set(self.controller.lang)
        self.lang_cb.pack(side="left", padx=5)
        self.lang_cb.bind("<<ComboboxSelected>>", self.change_language)

    def change_language(self, event):
        """Оновлює всі тексти на екрані сейвів при зміні мови"""
        self.controller.lang = self.lang_cb.get()
        self.root.title(self.controller.t("start_title"))
        self.context_menu.entryconfig(0, label=self.controller.t("del_save"))
        
        for i in range(1, 6):
            self.update_slot_button(i)

    def get_btn_text(self, slot_id, exists):
        """Формує текст для кнопки (СЛОТ X - НОВА ГРА / ПРОДОВЖИТИ)"""
        status = self.controller.t("continue") if exists else self.controller.t("new_game")
        return f"{self.controller.t('slot')} {slot_id} - {status}"

    def create_slot_button(self, slot_id):
        path = f"saves/save_slot_{slot_id}.json"
        exists = os.path.exists(path)
        
        btn_text = self.get_btn_text(slot_id, exists)
        bg_color = self.pl_green if exists else "white"

        btn = tk.Button(
            self.buttons_frame, text=btn_text, font=("Segoe UI", 11, "bold"),
            bg=bg_color, width=35, pady=12, relief="flat", cursor="hand2",
            command=lambda s=slot_id: self.on_slot_selected(s)
        )
        btn.pack(pady=10)
        btn.bind("<Button-3>", lambda event, s=slot_id: self.show_context_menu(event, s))
        self.slot_buttons[slot_id] = btn

    def update_slot_button(self, slot_id):
        """Оновлює тільки текст існуючої кнопки"""
        path = f"saves/save_slot_{slot_id}.json"
        exists = os.path.exists(path)
        self.slot_buttons[slot_id].config(text=self.get_btn_text(slot_id, exists))

    def show_context_menu(self, event, slot_id):
        path = f"saves/save_slot_{slot_id}.json"
        if os.path.exists(path):
            self.selected_slot_to_delete = slot_id
            self.context_menu.post(event.x_root, event.y_root)

    def confirm_delete(self):
        slot = self.selected_slot_to_delete
        if slot and messagebox.askyesno(self.controller.t("del_save"), f"{self.controller.t('del_confirm')} {slot}?"):
            path = f"saves/save_slot_{slot}.json"
            try:
                os.remove(path)
                self.update_slot_button(slot)
                self.slot_buttons[slot].config(bg="white")
                messagebox.showinfo(self.controller.t("done"), f"{self.controller.t('slot')} {slot} {self.controller.t('empty_slot')}")
            except Exception as e:
                messagebox.showerror("Error", f"{self.controller.t('del_err')} {e}")