import json
import os
import random
from datetime import datetime, timedelta
from models.models import Player, Team
from models.match_engine import MatchEngine
import sys

def resource_path(relative_path):
    """ Отримує шлях до ресурсу, працює для dev-режиму та для PyInstaller """
    try:
       
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainController:
    def __init__(self):
        self.teams = []
        self.current_user_team = None
        self.data_path = os.path.join('data', 'data.json')
        self.save_dir = 'saves'
        self.current_slot = 1
        
        #ІСТОРІЯ ТРАНСФЕРІВ
        self.transfer_history = [] 
        
        self.schedule = {} 
        self.game_date = datetime(2024, 8, 1)
        self.current_round = 1
        self.active_lineup = {} 
        self.team_style = "Medium"
        self.last_year_updated = 2024 

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.lang = "UKR" # Мова за замовчуванням
       
        
        self.texts = {
            "UKR": {
                "squad": " МІЙ СКЛАД ", "market": " ТРАНСФЕРИ ", 
                "table": " ТАБЛИЦЯ ", "history": " ІСТОРІЯ ТРАНСФЕРІВ ",
                "search": "Пошук:", "buy": "ПІДПИСАТИ", "play": "ПЕРЕЙТИ ДО МАТЧУ",
                "budget": "Бюджет:", "saved": "Гру збережено!",
                "th_player": "ГРАВЕЦЬ", "th_age": "ВІК", "th_pos": "ПОЗ", 
                "th_rating": "РЕЙТ", "th_fatigue": "ВТОМА", "th_price": "ЦІНА",
                "th_club": "КЛУБ", "th_p": "І", "th_w": "В", "th_d": "Н", "th_l": "П",
                "th_gf": "З", "th_ga": "Пр", "th_gd": "+/-", "th_pts": "ОЧКИ",
                "th_date": "ДАТА", "th_from": "ЗВІДКИ", "th_to": "КУДИ",
                "lbl_date": "Дата:", "lbl_round": "Тур:",
                "tac_title": "Тактика та Склад", "tac_confirm": "ПІДТВЕРДИТИ ТА ГРАТИ",
                "tac_offside": "Штучний офсайд", "tac_pressing": "Лінія пресингу:",
                "tac_def": "Захист", "tac_med": "Баланс", "tac_att": "Атака",
                "tac_err": "Потрібно 11 гравців!",
                "start_title": "Football Manager 2026 - Сейви",
                "slot": "СЛОТ", "new_game": "НОВА ГРА", "continue": "ПРОДОВЖИТИ",
                "del_save": "Видалити збереження", "del_confirm": "Ви впевнені, що хочете видалити збереження у слоті",
                "done": "Готово", "empty_slot": "тепер порожній.", "del_err": "Не вдалося видалити файл:",
                "match_summary": "Підсумок матчу", "match_at": "Матч на", 
                "stadium_rev": "ДОХІД СТАДІОНУ", "match_res": "Результат:", "btn_continue": "ПРОДОВЖИТИ",
                "win": "Перемога", "draw": "Нічия", "loss": "Поразка",
                "exit_save": "ВИЙТИ ТА ЗБЕРЕГТИ"
            },
            "ENG": {
                "squad": " MY SQUAD ", "market": " TRANSFERS ", 
                "table": " STANDINGS ", "history": " TRANSFER HISTORY ",
                "search": "Search:", "buy": "SIGN PLAYER", "play": "PLAY MATCH",
                "budget": "Budget:", "saved": "Game saved!",
                "th_player": "PLAYER", "th_age": "AGE", "th_pos": "POS", 
                "th_rating": "RTG", "th_fatigue": "FATIGUE", "th_price": "PRICE",
                "th_club": "CLUB", "th_p": "P", "th_w": "W", "th_d": "D", "th_l": "L",
                "th_gf": "GF", "th_ga": "GA", "th_gd": "GD", "th_pts": "PTS",
                "th_date": "DATE", "th_from": "FROM", "th_to": "TO",
                "lbl_date": "Date:", "lbl_round": "Round:",
                "tac_title": "Tactics & Squad", "tac_confirm": "CONFIRM & PLAY",
                "tac_offside": "Offside Trap", "tac_pressing": "Pressing Line:",
                "tac_def": "Defend", "tac_med": "Balanced", "tac_att": "Attack",
                "tac_err": "Need 11 players!",
                "start_title": "Football Manager 2026 - Saves",
                "slot": "SLOT", "new_game": "NEW GAME", "continue": "CONTINUE",
                "del_save": "Delete save game", "del_confirm": "Are you sure you want to delete save in slot",
                "done": "Done", "empty_slot": "is now empty.", "del_err": "Failed to delete file:",
                "match_summary": "Match Summary", "match_at": "Match at", 
                "stadium_rev": "STADIUM REVENUE", "match_res": "Result:", "btn_continue": "CONTINUE",
                "win": "Win", "draw": "Draw", "loss": "Loss",
                "exit_save": "SAVE & EXIT"
            }
        }

    def t(self, key):
        """Метод для отримання тексту вибраною мовою"""
        return self.texts[self.lang].get(key, key)

    def load_data(self):
        try:
            if not os.path.exists(self.data_path): return False
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.teams = [] 
            for t_d in data['teams']:
                team = Team(t_d['name'], t_d['budget'], t_d.get('stadium_name', "Stadium"), t_d.get('capacity', 30000))
                for p_d in t_d['players']:
                    # При створенні нового гравця голи/асист за замовчуванням 0 (має бути в моделі)
                    player = Player(p_d['id'], p_d['name'], p_d['age'], p_d['position'], p_d['rating'], p_d['price'])
                    team.add_player(player)
                self.teams.append(team)
            self.generate_calendar()
            return True
        except Exception as e:
            print(f"Помилка завантаження: {e}")
            return False

    #СИСТЕМА ЗБЕРЕЖЕНЬ
    def save_game(self):
        path = os.path.join(self.save_dir, f"save_slot_{self.current_slot}.json")
        data = {
            "game_date": self.game_date.strftime("%Y-%m-%d"),
            "current_round": self.current_round,
            "last_year_updated": self.last_year_updated,
            "user_team_name": self.current_user_team.name if self.current_user_team else None,
            "transfer_history": self.transfer_history, # Зберігаємо історію
            "teams": [t.to_dict() for t in self.teams]
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_game(self, slot):
        self.current_slot = slot
        path = os.path.join(self.save_dir, f"save_slot_{slot}.json")
        if not os.path.exists(path): return False
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.game_date = datetime.strptime(data["game_date"], "%Y-%m-%d")
            self.current_round = data["current_round"]
            self.last_year_updated = data.get("last_year_updated", 2024)
            self.transfer_history = data.get("transfer_history", []) # Завантажуємо історію
            
            self.teams = []
            for t_d in data["teams"]:
                team = Team(t_d['name'], t_d['budget'], t_d['stadium_name'], t_d['capacity'])
                team.played, team.wins, team.draws, team.losses = t_d['played'], t_d['wins'], t_d['draws'], t_d['losses']
                team.gf, team.ga, team.points = t_d['gf'], t_d['ga'], t_d['points']
                for p_d in t_d['players']:
                    p = Player(p_d['id'], p_d['name'], p_d['age'], p_d['position'], p_d['rating'], p_d['price'])
                    p.fatigue = p_d.get('fatigue', 0)
                    p.goals = p_d.get('goals', 0) # Завантажуємо голи
                    p.assists = p_d.get('assists', 0) # Завантажуємо асисти
                    team.add_player(p)
                self.teams.append(team)
                if team.name == data["user_team_name"]: self.current_user_team = team
            self.generate_calendar()
            return True
        except: return False

    # ЦИКЛ СЕЗОНУ---
    def play_current_round(self):
        if self.current_round > 38: return "SEASON_END"

        if self.game_date.year > self.last_year_updated and self.game_date.month >= 1:
            for team in self.teams:
                for player in team.players:
                    player.grow_older()
            self.last_year_updated = self.game_date.year

        played_ids = [p.id for p in self.active_lineup.values() if p]
        for p in self.current_user_team.players:
            if p.id in played_ids:
                p.fatigue = min(5, p.fatigue + 1) if p.age <= 23 else min(10, p.fatigue + 2)
            else:
                p.fatigue = max(0, p.fatigue - 2)

        round_matches = self.schedule[self.current_round]
        user_res = None
        for h, a in round_matches:
            
            h_g, a_g, h_events, a_events = MatchEngine.simulate_match(h, a)
            
            rev = h.capacity * random.randint(5, 20)
            h.budget += rev
            h.played += 1; a.played += 1
            h.gf += h_g; h.ga += a_g; a.gf += a_g; a.ga += h_g
            
            if h_g > a_g: h.points += 3; h.wins += 1; a.losses += 1
            elif h_g == a_g: h.points += 1; a.points += 1; h.draws += 1; a.draws += 1
            else: a.points += 3; a.wins += 1; h.losses += 1

            if h == self.current_user_team or a == self.current_user_team:
                is_home = (h == self.current_user_team)
                res_text = "НІЧИЯ"
                if h_g > a_g: res_text = "ПЕРЕМОГА" if is_home else "ПОРАЗКА"
                elif a_g > h_g: res_text = "ПОРАЗКА" if is_home else "ПЕРЕМОГА"
                
                user_res = {
                    "home_team": h.name, "away_team": a.name, 
                    "home_score": h_g, "away_score": a_g, 
                    "home_events": h_events, "away_events": a_events, # Для вікна матчу
                    "stadium": h.stadium_name, "revenue": rev if is_home else 0, "result": res_text
                }

        self.current_round += 1
        self.game_date += timedelta(days=7)
        self.save_game()
        return user_res

    def process_season_end(self):
        sorted_teams = sorted(self.teams, key=lambda t: (t.points, t.gf - t.ga), reverse=True)
        prizes = {1: 100_000_000, 2: 70_000_000, 3: 50_000_000, 4: 40_000_000, 5: 20_000_000}
        for rank, team in enumerate(sorted_teams, 1):
            if rank in prizes: team.budget += prizes[rank]
            team.reset_stats() # Метод reset_stats має обнуляти голи гравців
        
        self.run_ai_transfers()
        self.current_round = 1
        self.game_date = datetime(self.game_date.year, 8, 1)
        self.generate_calendar()
        self.save_game()

    #ТРАНСФЕРИ З ІСТОРІЄЮ
    def process_buy_transaction(self, p, s_t):
        can, msg = self.current_user_team.can_buy_player(p)
        if can:
            # Додаємо запис в історію
            self.transfer_history.append({
                "date": self.game_date.strftime("%d.%m.%Y"),
                "player": p.name,
                "from": s_t.name,
                "to": self.current_user_team.name,
                "price": f"{p.price:,} $"
            })
            
            self.current_user_team.budget -= p.price; s_t.budget += p.price
            s_t.players.remove(p); self.current_user_team.players.append(p)
            self.save_game()
            return True, "Куплено!"
        return False, msg

    def process_sell_transaction(self, p):
        # Можна також додати запис про продаж в історію за бажанням
        self.transfer_history.append({
            "date": self.game_date.strftime("%d.%m.%Y"),
            "player": p.name,
            "from": self.current_user_team.name,
            "to": "Free Market",
            "price": f"{p.price:,} $"
        })
        self.current_user_team.budget += p.price
        self.current_user_team.players.remove(p)
        self.save_game()
        return True, "Продано!"

    def run_ai_transfers(self):
        all_market = self.get_all_market_players()
        for team in self.teams:
            if team == self.current_user_team: continue
            for _ in range(2):
                if not all_market: break
                random.shuffle(all_market)
                for cand in all_market:
                    p, seller = cand['player'], cand['team_object']
                    if team.budget >= p.price:
                        # Логуємо і для ШІ
                        self.transfer_history.append({
                            "date": self.game_date.strftime("%d.%m.%Y"),
                            "player": p.name, "from": seller.name, "to": team.name,
                            "price": f"{p.price:,} $"
                        })
                        team.budget -= p.price; seller.budget += p.price
                        seller.players.remove(p); team.add_player(p)
                        all_market.remove(cand); break

    def generate_calendar(self):
        temp_teams = self.teams[:]
        n = len(temp_teams)
        for r in range(n - 1):
            matches = []
            for i in range(n // 2):
                h, a = temp_teams[i], temp_teams[n-1-i]
                matches.append((a, h) if r % 2 else (h, a))
            self.schedule[r + 1] = matches
            temp_teams.insert(1, temp_teams.pop())
        for r in range(1, n):
            self.schedule[r + 19] = [(a, h) for h, a in self.schedule[r]]

    def get_all_market_players(self):
        m = []
        for t in self.teams:
            for p in t.players: m.append({"player": p, "team_name": t.name, "team_object": t})
        return m

    def get_all_teams_names(self):
        return sorted([t.name for t in self.teams])

    def select_team(self, name):
        for t in self.teams:
            if t.name == name:
                self.current_user_team = t
                return t
        return None
    def process_buy_transaction(self, player, seller_team):
        
        if seller_team == self.current_user_team:
            return False, "Ви не можете купувати гравців у власного клубу!"

        
        success, message = self.current_user_team.can_buy_player(player)
        
        if success:
            # Запис в історію трансферів
            self.transfer_history.append({
                "date": self.game_date.strftime("%d.%m.%Y"),
                "player": player.name,
                "from": seller_team.name,
                "to": self.current_user_team.name,
                "price": f"{player.price:,} $"
            })
            
            # Сама транзакція
            self.current_user_team.budget -= player.price
            seller_team.budget += player.price
            
            seller_team.players.remove(player)
            self.current_user_team.players.append(player)
            
            self.save_game()
            return True, f"Трансфер завершено! {player.name} підписав контракт."
            
        return False, message