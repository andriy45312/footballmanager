import random

class MatchEngine:
    @staticmethod
    def simulate_match(home_team, away_team):
        """
        Симулює матч: рахунок + автори голів та асистів.
        """
        
        home_rating = home_team.get_avg_rating()
        away_rating = away_team.get_avg_rating()

        
        home_eff = home_rating * 1.07
        away_eff = away_rating

        diff = home_eff - away_eff
        
        
        if home_team.style == "Defending":
            win_c, draw_c, lose_c = 35, 45, 20
        elif home_team.style == "Attacking":
            win_c, draw_c, lose_c = 30, 20, 50
        else: 
            win_c, draw_c, lose_c = 45, 20, 35

        
        win_c += diff * 3
        lose_c -= diff * 3
        
        win_c = max(5, min(90, win_c))
        lose_c = max(5, min(90, lose_c))
        
        roll = random.randint(1, 100)
        
        
        if roll <= win_c:
            home_goals = random.randint(1, 4)
            away_goals = random.randint(0, home_goals - 1)
        elif roll <= (win_c + draw_c):
            home_goals = random.randint(0, 2)
            away_goals = home_goals
        else:
            away_goals = random.randint(1, 4)
            home_goals = random.randint(0, away_goals - 1)

        
        if home_team.style == "Attacking":
            if random.random() > 0.5:
                home_goals += 1
                away_goals += 1

        # 3. РОЗПОДІЛ ГОЛІВ ТА АСИСТІВ МІЖ ГРАВЦЯМИ
        home_events = MatchEngine.assign_player_stats(home_team, home_goals)
        away_events = MatchEngine.assign_player_stats(away_team, away_goals)

        return home_goals, away_goals, home_events, away_events

    @staticmethod
    def assign_player_stats(team, goals_count):
        """
        Розподіляє голи та асисти всередині команди.
        Гарантує:
        - Кількість голів гравців = рахунок команди.
        - Ваги залежать від позиції та рейтингу.
        - Капи: 50 голів та 30 асистів за сезон.
        """
        events = []
        if goals_count == 0:
            return events

        
        players = team.players 

        for _ in range(goals_count):
            
            scorer_weights = []
            for p in players:
                
                weight = 10 if p.position == "FWD" else (4 if p.position == "MID" else 1)
                
                weight *= (p.current_rating / 50)
                
                if p.goals >= 50:
                    weight = 0
                scorer_weights.append(weight)

            
            if sum(scorer_weights) == 0: scorer_weights = [1] * len(players)
            
            scorer = random.choices(players, weights=scorer_weights, k=1)[0]
            scorer.goals += 1

            
            assister_weights = []
            for p in players:
                
                weight = 10 if p.position == "MID" else (5 if p.position == "FWD" else 2)
                weight *= (p.current_rating / 50)
               
                if p.assists >= 30:
                    weight = 0
                assister_weights.append(weight)

            if sum(assister_weights) == 0: assister_weights = [1] * len(players)
            
            assister = random.choices(players, weights=assister_weights, k=1)[0]
            
            event_type = "Goal"
            
            if assister.id == scorer.id:
                event_type = "Penalty/Set-piece"
                
            else:
                assister.assists += 1
            
            events.append({
                "scorer": scorer.name,
                "assister": assister.name,
                "type": event_type
            })

        return events