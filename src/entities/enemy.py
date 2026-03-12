import pygame
import math
import random
import config

class Enemy:
    def __init__(self, x, y, enemy_type='gang_member'):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.angle = 0
        self.health = 50 if enemy_type == 'gang_member' else 100
        self.max_health = self.health
        
        # Movement
        self.walking_speed = 80
        self.running_speed = 120
        
        # Visual
        self.width = 16
        self.height = 32
        self.color = (200, 50, 50)  # Red for enemies
        
        # AI
        self.state = 'idle'  # idle, chase, attack, flee
        self.state_timer = 0
        self.target = None
        self.attack_range = 100
        self.chase_range = 300
        self.flee_range = 50
        
        # Combat
        self.weapon = 'pistol'
        self.attack_cooldown = 0
        self.damage = 15
        
        # Money reward
        self.money = random.randint(10, 100)
        
    def update(self, dt, player_pos, buildings):
        self.state_timer -= dt
        self.attack_cooldown -= dt
        
        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        # AI state machine
        if dist < self.flee_range:
            self.state = 'flee'
        elif dist < self.attack_range:
            self.state = 'attack'
        elif dist < self.chase_range:
            self.state = 'chase'
        else:
            self.state = 'idle'
            
        # Execute state behavior
        if self.state == 'idle':
            self.idle_behavior(dt)
        elif self.state == 'chase':
            self.chase_behavior(dt, dx, dy, dist)
        elif self.state == 'attack':
            self.attack_behavior(dt, dx, dy)
        elif self.state == 'flee':
            self.flee_behavior(dt, dx, dy, dist)
            
        # Face the player
        if dist > 0:
            self.angle = math.degrees(math.atan2(-dy, dx))
            
    def idle_behavior(self, dt):
        if self.state_timer <= 0:
            # Random movement
            if random.random() < 0.02:
                self.state_timer = random.uniform(2, 5)
                self.target = None
                
    def chase_behavior(self, dt, dx, dy, dist):
        # Move toward player
        if dist > 0:
            move_x = dx / dist * self.running_speed * dt
            move_y = dy / dist * self.running_speed * dt
            self.x += move_x
            self.y += move_y
            
    def attack_behavior(self, dt, dx, dy):
        # Stop and shoot
        if self.attack_cooldown <= 0:
            self.attack_cooldown = random.uniform(0.5, 1.5)
            # Return bullet info
            return True, self.angle, self.damage
        return False, 0, 0
        
    def flee_behavior(self, dt, dx, dy, dist):
        # Move away from player
        if dist > 0:
            move_x = -dx / dist * self.running_speed * dt
            move_y = -dy / dist * self.running_speed * dt
            self.x += move_x
            self.y += move_y
            
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True  # Dead
        return False
        
    def draw(self, screen, camera):
        cx = self.x - camera.x
        cy = self.y - camera.y
        
        # Draw body
        pygame.draw.rect(screen, self.color,
                        (cx - self.width//2, cy - self.height//2,
                         self.width, self.height))
                         
        # Direction indicator
        rad = math.radians(self.angle)
        end_x = cx + 15 * math.cos(rad)
        end_y = cy - 15 * math.sin(rad)
        pygame.draw.line(screen, (255, 255, 0), (cx, cy), (end_x, end_y), 2)
        
        # Health bar
        if self.health < self.max_health:
            bar_width = 20
            bar_height = 4
            health_pct = self.health / self.max_health
            
            pygame.draw.rect(screen, (100, 0, 0),
                           (cx - bar_width//2, cy - self.height//2 - 10,
                            bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0),
                           (cx - bar_width//2, cy - self.height//2 - 10,
                            bar_width * health_pct, bar_height))
                            
    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Gang:
    def __init__(self, x, y, name, color):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.members = []
        self.vehicles = []
        
    def add_member(self, enemy):
        enemy.color = self.color
        self.members.append(enemy)
        
    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        
    def update(self, dt, player_pos, buildings):
        for member in self.members:
            if member.health > 0:
                member.update(dt, player_pos, buildings)
                
    def draw(self, screen, camera):
        for member in self.members:
            if member.health > 0:
                member.draw(screen, camera)


class EnemyVehicle:
    def __init__(self, x, y, car_type):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.car_type = car_type
        
        config_data = config.CAR_CONFIG.get(car_type, config.CAR_CONFIG['default'])
        self.max_speed = config_data['max_speed']
        self.acceleration = config_data['acceleration']
        self.color = config_data['color']
        self.width = config_data['width']
        self.height = config_data['height']
        
        # AI
        self.state = 'patrol'
        self.target = None
        self.patrol_points = []
        
        # Combat
        self.health = 200
        self.max_health = 200
        
    def update(self, dt, player_pos):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 200:
            self.state = 'chase'
        elif dist > 500:
            self.state = 'patrol'
            
        if self.state == 'chase':
            if dist > 0:
                target_angle = math.degrees(math.atan2(-dy, dx))
                angle_diff = (target_angle - self.angle + 180) % 360 - 180
                
                if abs(angle_diff) > 10:
                    self.angle += angle_diff * 3 * dt
                    
                self.speed += self.acceleration * dt
                self.speed = min(self.speed, self.max_speed * 0.8)
                
        elif self.state == 'patrol':
            self.speed *= 0.95
            
        # Movement
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad) * dt
        self.y += self.speed * math.cos(rad) * dt
        
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
        
    def draw(self, screen, camera):
        # Similar to Car draw
        points = [(-self.width/2, -self.height/2),
                  (self.width/2, -self.height/2),
                  (self.width/2, self.height/2),
                  (-self.width/2, self.height/2)]
        
        rotated_points = []
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        cx, cy = self.x - camera.x, self.y - camera.y
        
        for px, py in points:
            rx = px * cos_a - py * sin_a + cx
            ry = px * sin_a + py * cos_a + cy
            rotated_points.append((rx, ry))
            
        pygame.draw.polygon(screen, self.color, rotated_points)
        
        # Health bar
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            health_pct = self.health / self.max_health
            
            pygame.draw.rect(screen, (100, 0, 0),
                           (cx - bar_width//2, cy - self.height//2 - 10,
                            bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0),
                           (cx - bar_width//2, cy - self.height//2 - 10,
                            bar_width * health_pct, bar_height))
                            
    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


# Spawn functions
def create_gang_territory(center_x, center_y, name, color, member_count):
    gang = Gang(center_x, center_y, name, color)
    
    for _ in range(member_count):
        offset_x = random.randint(-150, 150)
        offset_y = random.randint(-150, 150)
        enemy = Enemy(center_x + offset_x, center_y + offset_y)
        enemy.color = color
        gang.add_member(enemy)
        
    return gang

