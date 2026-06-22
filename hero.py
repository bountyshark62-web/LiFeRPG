# hero.py
import json
import os
import random

class Hero:
    def __init__(self):
        self.name = "ГЕРОЙ"
        self.age_group = "adult"
        
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.gold = 50
        self.hp = 100
        
        self.skills = {"strength": 0, "wisdom": 0, "order": 0}
        
        self.body_color_idx = 0
        self.hair_style_idx = 0
        self.shirt_idx = 0
        
        self.daily_quests = []
        self.completed_today = []
        
        self.boss_name = "ДРАКОН ЛЕНИ"
        self.boss_hp = 300
        self.boss_max_hp = 300

        self.body_colors = ["Светлая кожа", "Загорелая", "Темная кожа", "Зеленая (Орк!)"]
        self.hair_styles = ["Лысый", "Короткие", "Длинные", "Ирокез"]
        self.shirts = ["Стартовая майка", "Куртка", "Роба мага", "Броня"]
        
        # МАГАЗИН: Купленные вещи (0 - не куплено, 1 - куплено)
        self.inventory = {"Куртка": 0, "Роба мага": 0, "Броня": 0}
        self.shop_prices = {"Куртка": 30, "Роба мага": 60, "Броня": 100}

    def next_body(self): self.body_color_idx = (self.body_color_idx + 1) % len(self.body_colors)
    def next_hair(self): self.hair_style_idx = (self.hair_style_idx + 1) % len(self.hair_styles)
    def next_shirt(self): self.shirt_idx = (self.shirt_idx + 1) % len(self.shirts)

    def buy_item(self, item_name, idx):
        """Покупка одежды в магазине"""
        if self.inventory.get(item_name) == 1:
            self.shirt_idx = idx # Если куплено, просто надеваем
            return True
        price = self.shop_prices.get(item_name, 999)
        if self.gold >= price:
            self.gold -= price
            self.inventory[item_name] = 1
            self.shirt_idx = idx
            return True
        return False

    def generate_5_quests(self):
        try:
            with open("quests.json", "r", encoding="utf-8") as f:
                database = json.load(f)
            pool = database.get(self.age_group, database["adult"])
            today = []
            today.extend(random.sample(pool["base"], min(2, len(pool["base"]))))
            today.extend(random.sample(pool["medium"], min(2, len(pool["medium"]))))
            today.extend(random.sample(pool["hard"], min(1, len(pool["hard"]))))
            self.daily_quests = today
            self.completed_today = []
        except Exception as e:
            print("Ошибка генерации:", e)

    def complete_quest(self, quest_id):
        if quest_id in self.completed_today: return
        for q in self.daily_quests:
            if q["id"] == quest_id:
                self.completed_today.append(quest_id)
                
                # Множители от надетой одежды
                multiplier = 1.0
                if self.shirt_idx == 1: multiplier = 1.2  # Куртка дает +20% опыта
                if self.shirt_idx == 2: multiplier = 1.5  # Роба мага дает +50% опыта
                if self.shirt_idx == 3: multiplier = 2.0  # Броня дает х2 к опыту!
                
                g_reward = q["gold"]
                xp_reward = int(q["xp"] * multiplier)
                
                self.gold += g_reward
                self.xp += xp_reward
                self.boss_hp = max(0, self.boss_hp - xp_reward)
                
                skill = q.get("skill", "wisdom")
                if skill in self.skills: self.skills[skill] += xp_reward
                
                if self.xp >= self.xp_to_next_level:
                    self.xp -= self.xp_to_next_level
                    self.level += 1
                    self.xp_to_next_level = int(self.xp_to_next_level * 1.2)
                    self.gold += 20
                break

    def save_to_file(self):
        data = {
            "level": self.level, "xp": self.xp, "xp_to_next_level": self.xp_to_next_level, 
            "gold": self.gold, "hp": self.hp, "skills": self.skills, "age_group": self.age_group,
            "body_idx": self.body_color_idx, "hair_idx": self.hair_style_idx, "shirt_idx": self.shirt_idx,
            "daily_quests": self.daily_quests, "completed_today": self.completed_today,
            "boss_hp": self.boss_hp, "inventory": self.inventory
        }
        with open("save_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_file(self):
        if os.path.exists("save_data.json"):
            try:
                with open("save_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.level = data.get("level", self.level)
                self.xp = data.get("xp", self.xp)
                self.xp_to_next_level = data.get("xp_to_next_level", self.xp_to_next_level)
                self.gold = data.get("gold", self.gold)
                self.hp = data.get("hp", self.hp)
                self.skills = data.get("skills", self.skills)
                self.age_group = data.get("age_group", self.age_group)
                self.body_color_idx = data.get("body_idx", self.body_color_idx)
                self.hair_style_idx = data.get("hair_idx", self.hair_style_idx)
                self.shirt_idx = data.get("shirt_idx", self.shirt_idx)
                self.daily_quests = data.get("daily_quests", [])
                self.completed_today = data.get("completed_today", [])
                self.boss_hp = data.get("boss_hp", self.boss_hp)
                self.inventory = data.get("inventory", self.inventory)
                return True
            except: pass
        return False
