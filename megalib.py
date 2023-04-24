import random

class Player:
    def __init__(self, name: str, x = None, y = None):
        self.name = name
        self.O2_level = 100
        self.x = x
        self.y = y
        
    def O2_depletion(self, time):
        self.O2_level -= 1 * time//10
        
        if self.O2_level <= 0:
            return False
        
        return True
        
    def collect_O2(self):
        self.O2_level += 20 if self.O2_level + 20 <= 100 else 100
        
    def move_up(self):
        self.y += 1
        
    def move_down(self):
        self.y -= 1
        
    def move_right(self):
        self.x += 1
        
    def move_left(self):
        self.y -= 1

class Map:
    def __init__(self):
        self.data = [[]]

class O2Tanks:
    def __init__(self):
        self.O2_tanks = list()
        self.O2_generator = O2TankGenerator()
        
    def create_tanks(self, num):
        self.empty_list()
        
        for _ in range(num):
            self.O2_tanks.append(self.O2_generator.generate())
        
    def empty_list(self):
        self.O2_tanks = list()

class O2Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class O2TankGenerator:
    def __init__(self):
        pass
        
    def generate(self):
        x = random.randint(0, 64)
        y = random.randint(0, 64)
        
        return O2Tank(x, y)

class FireExtinguisher:
    pass