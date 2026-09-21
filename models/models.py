import random

class Player:
    def __init__(self, player_id, name, age, position, rating, price):
        self.id = player_id
        self.name = name
        self.age = age
        self.position = position 
        self.rating = rating
        self.price = price
        self.fatigue = 0
        
        self.goals = 0
        self.assists = 0

    @property
    def current_rating(self):
        return max(1, self.rating - self.fatigue)

    def update_price(self):
        base = self.rating * 1_500_000 
        age_mod = 1.5 if self.age < 22 else (1.1 if self.age < 29 else (0.7 if self.age < 33 else 0.4))
        self.price = int(base * age_mod)

    def grow_older(self):
        self.age += 1
        if self.age <= 24: self.rating += random.randint(2, 5)
        elif self.age <= 29: self.rating += random.randint(-1, 2)
        else: self.rating -= random.randint(1, 4)
        self.rating = max(5, min(99, self.rating))
        self.update_price()
        
        self.goals = 0
        self.assists = 0

    def to_dict(self):
        return self.__dict__

class Team:
    def __init__(self, name, budget, stadium_name="Stadium", capacity=30000):
        self.name, self.budget, self.stadium_name, self.capacity = name, budget, stadium_name, capacity
        self.players = []
        self.style = "Medium"
        self.played = self.wins = self.draws = self.losses = 0
        self.gf = self.ga = self.points = 0

    def add_player(self, player):
        self.players.append(player)

    def get_avg_rating(self):
        if not self.players: return 0
        return sum(p.current_rating for p in self.players) / len(self.players)

    def can_buy_player(self, player):
        if self.budget < player.price: return False, "Мало грошей!"
        if len(self.players) >= 33: return False, "Склад повний!"
        return True, "OK"

    def can_sell_player(self, player):
        if len(self.players) <= 11: return False, "Мінімум 11 гравців!"
        return True, "OK"

    def reset_stats(self):
        self.played = self.wins = self.draws = self.losses = self.gf = self.ga = self.points = 0
        for p in self.players:
            p.goals = 0
            p.assists = 0

    def to_dict(self):
        team_data = self.__dict__.copy()
        team_data['players'] = [p.to_dict() for p in self.players]
        return team_data
    def can_buy_player(self, player):
        
        if any(p.id == player.id for p in self.players):
            return False, "Цей гравець вже є у вашому складі!"
            
        if self.budget < player.price: 
            return False, f"Недостатньо коштів! Потрібно {player.price:,} $."
            
        if len(self.players) >= 33: 
            return False, "Заявка переповнена! Максимум 33 гравці."
            
        return True, "OK"