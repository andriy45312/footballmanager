import os
import flet as ft
from controllers.main_controller import MainController

def main(page: ft.Page):
    page.title = "Football Manager 2026 Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 450
    page.window.height = 800

    ctrl = MainController()
    
    PL_PURPLE = "#3d195b"
    PL_GREEN = "#00ff85"

    # ==========================================
    # ЕКРАН 1: СИСТЕМА СЕЙВІВ
    # ==========================================
    def show_start_screen():
        page.controls.clear()
        slots_col = ft.Column(spacing=15, alignment="center", horizontal_alignment="center")
        
        for i in range(1, 6):
            path = os.path.join(ctrl.save_dir, f"save_slot_{i}.json")
            exists = os.path.exists(path)
            
            btn_text = f"СЛОТ {i} - ПРОДОВЖИТИ" if exists else f"СЛОТ {i} - НОВА ГРА"
            btn_color = PL_GREEN if exists else "white"
            btn_text_color = "black"
            
            def on_slot_click(e, slot=i, ex=exists):
                ctrl.current_slot = slot
                if ex:
                    if ctrl.load_game(slot):
                        show_dashboard()
                else:
                    if ctrl.load_data():
                        show_team_selection()

            slots_col.controls.append(
                ft.ElevatedButton(
                    content=ft.Text(btn_text, weight="bold", color=btn_text_color),
                    bgcolor=btn_color,
                    width=300, height=50,
                    on_click=on_slot_click
                )
            )

        layout = ft.Container(
            content=ft.Column([
                ft.Container(height=50),
                ft.Text("PREMIER LEAGUE", size=28, weight="bold", color=PL_GREEN, text_align="center"),
                ft.Text("Football Manager 2026", size=16, color="white70"),
                ft.Container(height=40),
                slots_col
            ], horizontal_alignment="center"),
            bgcolor=PL_PURPLE, expand=True, alignment=ft.alignment.top_center
        )
        page.add(layout)

    # ==========================================
    # ЕКРАН 2: ВИБІР КОМАНДИ
    # ==========================================
    def show_team_selection():
        page.controls.clear()
        teams_list = ft.ListView(expand=True, spacing=5)
        for t_name in ctrl.get_all_teams_names():
            teams_list.controls.append(
                ft.ListTile(
                    title=ft.Text(t_name, weight="bold"),
                    trailing=ft.Text(">", size=16, weight="bold"),
                    on_click=lambda e, name=t_name: select_team_and_start(name)
                )
            )

        layout = ft.Column([
            ft.Container(
                content=ft.Text("ОБЕРІТЬ СВІЙ КЛУБ", size=20, weight="bold", color="white"),
                bgcolor=PL_PURPLE, padding=20, alignment="center"
            ),
            teams_list
        ], expand=True)
        page.add(layout)

    def select_team_and_start(team_name):
        if ctrl.select_team(team_name):
            ctrl.save_game()
            show_dashboard()

    # ==========================================
    # ЕКРАН 3: ДАШБОРД (Головне меню)
    # ==========================================
    def show_dashboard():
        page.controls.clear()
        team = ctrl.current_user_team
        current_tab = "squad"
        
        # Стан сортування для складу
        squad_sort = {"col": "current_rating", "asc": False}
        
        header_budget_lbl = ft.Text(f"Бюджет: €{team.budget:,}", color=PL_GREEN, weight="bold")
        
        def save_and_exit(e):
            ctrl.save_game()
            page.overlay.append(ft.SnackBar(ft.Text("Гру збережено!"), bgcolor="green800", open=True))
            page.update()
            try:
                page.window.destroy()
            except AttributeError:
                import sys
                sys.exit(0)

        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(team.name, size=22, weight="bold"),
                        ft.Text(team.stadium_name, size=12, color="white70"),
                    ], spacing=0),
                    ft.Row([
                        ft.ElevatedButton("ГРАТИ", bgcolor=PL_GREEN, color="black", on_click=lambda e: open_tactics_modal()),
                        ft.ElevatedButton("ВИХІД", bgcolor="red700", color="white", on_click=save_and_exit)
                    ], spacing=5)
                ], alignment="spaceBetween"),
                ft.Row([
                    header_budget_lbl,
                    ft.Text(f"Тур {ctrl.current_round} | {ctrl.game_date.strftime('%d.%m.%Y')}", color="white54", size=12)
                ], alignment="spaceBetween")
            ]),
            bgcolor=PL_PURPLE, padding=15
        )

        # --- ВКЛАДКА 1: СКЛАД (Зі статистикою і сортуванням) ---
        def get_squad_view():
            cols = [
                ("name", "Гравець"), ("age", "Вік"), ("position", "Поз"), 
                ("current_rating", "Рейт"), ("fatigue", "Втома"), 
                ("price", "Ціна"), ("goals", "⚽"), ("assists", "👟")
            ]

            def on_sort(e):
                col_key = cols[e.column_index][0]
                if squad_sort["col"] == col_key:
                    squad_sort["asc"] = not squad_sort["asc"]
                else:
                    squad_sort["col"] = col_key
                    squad_sort["asc"] = False
                set_tab("squad") 

            data_cols = [ft.DataColumn(ft.Text(label, weight="bold"), on_sort=on_sort) for _, label in cols]
            sort_idx = next((i for i, (k, _) in enumerate(cols) if k == squad_sort["col"]), 3)

            # Розумне сортування (числа або рядки)
            key = squad_sort["col"]
            sorted_players = sorted(
                team.players, 
                key=lambda p: getattr(p, key, 0) if not isinstance(getattr(p, key, 0), str) else getattr(p, key, ""), 
                reverse=not squad_sort["asc"]
            )

            rows = []
            for p in sorted_players:
                fatigue_val = getattr(p, 'fatigue', 0)
                fatigue_str = str(fatigue_val) if fatigue_val > 0 else "0"
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p.name, weight="bold")),
                    ft.DataCell(ft.Text(str(p.age))),
                    ft.DataCell(ft.Text(p.position)),
                    ft.DataCell(ft.Text(str(p.current_rating), weight="bold", color=PL_GREEN if p.current_rating >= 80 else "amber")),
                    ft.DataCell(ft.Text(fatigue_str, color="red400" if fatigue_val >= 5 else "white")),
                    ft.DataCell(ft.Text(f"€{p.price:,}")),
                    ft.DataCell(ft.Text(str(getattr(p, 'goals', 0)))),
                    ft.DataCell(ft.Text(str(getattr(p, 'assists', 0)))),
                ]))

            dt = ft.DataTable(
                columns=data_cols, rows=rows,
                sort_column_index=sort_idx, sort_ascending=squad_sort["asc"],
                column_spacing=15, data_row_max_height=40, heading_row_height=40
            )
            # Горизонтальний скрол для мобільних екранів
            return ft.ListView([ft.Row([dt], scroll="always")], expand=True)

        # --- ВКЛАДКА 2: РИНОК ---
        search_var = ft.TextField(hint_text="Пошук гравця...", height=40, text_size=13, expand=True)
        market_list = ft.ListView(expand=True)

        def refresh_market(e=None):
            market_list.controls.clear()
            query = search_var.value.lower() if search_var.value else ""
            for item in ctrl.get_all_market_players():
                p = item['player']
                seller = item['team_object']
                if query in p.name.lower():
                    market_list.controls.append(
                        ft.ListTile(
                            leading=ft.CircleAvatar(content=ft.Text(p.position, size=11)),
                            title=ft.Text(p.name, weight="bold"),
                            subtitle=ft.Text(f"{item['team_name']} | Рейт: {p.rating}\n€{p.price:,}", size=11),
                            trailing=ft.ElevatedButton("Купити", bgcolor=PL_GREEN, color="black", on_click=lambda e, pl=p, sl=seller: buy_player(pl, sl))
                        )
                    )
            page.update()

        search_var.on_change = refresh_market

        def get_market_view():
            refresh_market()
            return ft.Column([
                ft.Container(content=search_var, padding=10),
                market_list
            ], expand=True)

        def buy_player(player, seller):
            success, msg = ctrl.process_buy_transaction(player, seller)
            page.overlay.append(ft.SnackBar(ft.Text(msg), bgcolor="green800" if success else "red800", open=True))
            if success:
                header_budget_lbl.value = f"Бюджет: €{team.budget:,}"
                refresh_market()
                page.update()

        # --- ВКЛАДКА 3: ТАБЛИЦЯ ---
        def get_table_view():
            sorted_teams = sorted(ctrl.teams, key=lambda t: (t.points, (t.gf - t.ga), t.gf), reverse=True)
            rows = []
            for i, t in enumerate(sorted_teams):
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(i + 1))),
                    ft.DataCell(ft.Text(t.name, weight="bold" if t.name == team.name else "normal")),
                    ft.DataCell(ft.Text(str(t.played))),
                    ft.DataCell(ft.Text(str(t.points), weight="bold", color=PL_GREEN if t.name == team.name else None))
                ]))
            return ft.ListView([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("#")),
                        ft.DataColumn(ft.Text("Клуб")),
                        ft.DataColumn(ft.Text("І")),
                        ft.DataColumn(ft.Text("О")),
                    ],
                    rows=rows, column_spacing=15, data_row_max_height=40
                )
            ], expand=True)

        # --- ВКЛАДКА 4: ІСТОРІЯ ---
        def get_history_view():
            items = []
            for h in reversed(ctrl.transfer_history):
                items.append(
                    ft.ListTile(
                        title=ft.Text(h['player'], weight="bold"),
                        subtitle=ft.Text(f"{h['from']} ➔ {h['to']}\n{h['date']}", size=11),
                        trailing=ft.Text(h['price'], color="red300" if h['to'] == team.name else "green300", weight="bold")
                    )
                )
            return ft.ListView(controls=items, expand=True)

        # РОУТИНГ ТАБІВ
        content_area = ft.Container(content=get_squad_view(), expand=True)

        def set_tab(tab_name):
            nonlocal current_tab
            current_tab = tab_name
            btn_squad.bgcolor = "blue700" if tab_name == "squad" else "grey800"
            btn_market.bgcolor = "blue700" if tab_name == "market" else "grey800"
            btn_table.bgcolor = "blue700" if tab_name == "table" else "grey800"
            btn_history.bgcolor = "blue700" if tab_name == "history" else "grey800"
            
            if current_tab == "squad": content_area.content = get_squad_view()
            elif current_tab == "market": content_area.content = get_market_view()
            elif current_tab == "table": content_area.content = get_table_view()
            elif current_tab == "history": content_area.content = get_history_view()
            page.update()

        btn_squad = ft.ElevatedButton("Склад", color="white", bgcolor="blue700", on_click=lambda e: set_tab("squad"))
        btn_market = ft.ElevatedButton("Ринок", color="white", bgcolor="grey800", on_click=lambda e: set_tab("market"))
        btn_table = ft.ElevatedButton("Таблиця", color="white", bgcolor="grey800", on_click=lambda e: set_tab("table"))
        btn_history = ft.ElevatedButton("Історія", color="white", bgcolor="grey800", on_click=lambda e: set_tab("history"))

        nav_row = ft.Row([btn_squad, btn_market, btn_table, btn_history], alignment="center", scroll="auto")
        layout = ft.Column([header, nav_row, content_area], expand=True, spacing=0)
        page.add(layout)
        page.update()

        # ==========================================
        # МОДАЛКА: ТАКТИКА І МАТЧ
        # ==========================================
        def open_tactics_modal():
            if ctrl.current_round > 38:
                ctrl.process_season_end()
                page.overlay.append(ft.SnackBar(ft.Text("Новий сезон розпочато!"), bgcolor="green", open=True))
                show_dashboard()
                return

            style_dropdown = ft.Dropdown(
                options=[
                    ft.dropdown.Option("Defending", "Захист"),
                    ft.dropdown.Option("Medium", "Баланс"),
                    ft.dropdown.Option("Attacking", "Атака")
                ],
                value=ctrl.team_style, label="Стиль гри", width=200
            )

            def execute_match(e):
                ctrl.team_style = style_dropdown.value
                tactics_dlg.open = False
                res = ctrl.play_current_round()
                if res:
                    show_match_result(res)

            tactics_dlg = ft.AlertDialog(
                title=ft.Text("Підготовка до матчу"),
                content=ft.Column([
                    ft.Text("Оберіть стиль на наступну гру:"),
                    style_dropdown,
                    ft.Text("Склад формується автоматично з найсильніших.", size=11, color="grey400")
                ], tight=True),
                actions=[
                    ft.TextButton("Скасувати", on_click=lambda e: close_dlg(tactics_dlg)),
                    ft.ElevatedButton("СИМУЛЮВАТИ", bgcolor=PL_GREEN, color="black", on_click=execute_match)
                ]
            )
            page.overlay.append(tactics_dlg)
            tactics_dlg.open = True
            page.update()

        def show_match_result(res):
            h_goals = ft.Column([ft.Text(f"⚽ {ev['scorer']} ({ev['assister']})", size=12) for ev in res['home_events']])
            a_goals = ft.Column([ft.Text(f"⚽ {ev['scorer']} ({ev['assister']})", size=12) for ev in res['away_events']])

            res_dlg = ft.AlertDialog(
                title=ft.Text("Підсумок матчу", text_align="center"),
                content=ft.Column([
                    ft.Text(f"{res['stadium']}", size=11, color="grey400", text_align="center"),
                    ft.Text(f"{res['home_team']} {res['home_score']} - {res['away_score']} {res['away_team']}", size=22, weight="bold", text_align="center"),
                    ft.Divider(),
                    ft.Row([h_goals, a_goals], alignment="spaceBetween", vertical_alignment="start"),
                    ft.Divider(),
                    ft.Text(f"Квитки: +€{res.get('revenue', 0):,}", color=PL_GREEN, weight="bold")
                ], tight=True, horizontal_alignment="center"),
                actions=[ft.ElevatedButton("ПРОДОВЖИТИ", on_click=lambda e: end_match(res_dlg))],
                actions_alignment="center"
            )
            page.overlay.append(res_dlg)
            res_dlg.open = True
            page.update()

        def end_match(dlg):
            close_dlg(dlg)
            show_dashboard()

        def close_dlg(dlg):
            dlg.open = False
            page.update()

    show_start_screen()

if __name__ == "__main__":
    print(">>> СЕРВЕР ЗАПУЩЕНО ДЛЯ ТЕЛЕФОНУ!")
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)