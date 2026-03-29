import pygame
import math
import random
import config

class PoliceSystem:
    def __init__(self):
        self.wanted_level = 0
        self.max_wanted = 5
        self.police_vehicles = []
        self.police_officers = []
        self.last_crime_time = 0
        self.crime_heat = 0  # Accumulated heat from crimes
        
        # Wanted thresholds
        self.wanted_thresholds = {
            1: {'heat': 100, 'vehicles': 1, 'officers': 0},
            2: {'heat': 250, 'vehicles': 2, 'officers': 2},
            3: {'heat': 500, 'vehicles': 3, 'officers': 4},
            4: {'heat': 800, 'vehicles': 4, 'officers': 6},
            5: {'heat': 1200, 'vehicles': 6, 'officers': 8},
        }
        
    def add_crime(self, crime_value, position):
        """Add crime heat at position"""
        self.crime_heat += crime_value
        self.last_crime_time = pygame.time.get_ticks()
        
        # Check for wanted level increase
        new_level = self.calculate_wanted_level()
        if new_level > self.wanted_level:
            self.wanted_level = new_level
            self.spawn_police(position)
            
    def calculate_wanted_level(self):
        """Calculate wanted level based on heat"""
        for level in range(self.max_wanted, 0, -1):
            if self.crime_heat >= self.wanted_thresholds[level]['heat']:
                return level
        return 0
        
    def spawn_police(self, position):
        """Spawn police units based on wanted level"""
        if self.wanted_level == 0:
            return
            
        threshold = self.wanted_thresholds[self.wanted_level]
        
        # Spawn police vehicles
        needed_vehicles = threshold['vehicles'] - len(self.police_vehicles)
        for _ in range(needed_vehicles):
            angle = random.uniform(0, 360)
            offset = random.randint(300, 500)
            x = position[0] + offset * math.cos(math.radians(angle))
            y = position[1] + offset * math.sin(math.radians(angle))
            
            police_car = PoliceVehicle(x, y, self.wanted_level)
            self.police_vehicles.append(police_car)
            
        # Spawn police officers on foot
        needed_officers = threshold['officers'] - len(self.police_officers)
        for _ in range(needed_officers):
            angle = random.uniform(0, 360)
            offset = random.randint(200, 400)
            x = position[0] + offset * math.cos(math.radians(angle))
            y = position[1] + offset * math.sin(math.radians(angle))
            
            officer = PoliceOfficer(x, y)
            self.police_officers.append(officer)
            
    def update(self, dt, player_pos, world):
        """Update police AI"""
        # Update vehicles
        for vehicle in self.police_vehicles[:]:
            vehicle.update(dt, player_pos, world)
            if vehicle.health <= 0:
                self.police_vehicles.remove(vehicle)
                
        # Update officers
        for officer in self.police_officers[:]:
            officer.update(dt, player_pos, world)
            if officer.health <= 0:
                self.police_officers.remove(officer)
                
        # Reduce heat over time when not committing crimes
        time_since_crime = (pygame.time.get_ticks() - self.last_crime_time) / 1000
        if time_since_crime > 30:  # 30 seconds of no crimes
            self.crime_heat = max(0, self.crime_heat - int(dt * 10))
            new_level = self.calculate_wanted_level()
            if new_level < self.wanted_level:
                self.wanted_level = new_level
                
    def draw(self, screen, camera):
        for vehicle in self.police_vehicles:
            vehicle.draw(screen, camera)
        for officer in self.police_officers:
            officer.draw(screen, camera)
            
    def check_collisions(self, player_rect):
        """Check if player collides with police"""
        for vehicle in self.police_vehicles:
            if player_rect.colliderect(vehicle.get_rect()):
                return True, vehicle
        for officer in self.police_officers:
            if player_rect.colliderect(officer.get_rect()):
                return True, officer
        return False, None


class PoliceVehicle:
    def __init__(self, x, y, wanted_level):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.wanted_level = wanted_level
        
        # Police car properties
        self.max_speed = 350 + wanted_level * 30
        self.acceleration = 300
        self.drag = 2.0
        self.width = 44
        self.height = 24
        self.color = (20, 20, 80)
        self.health = 150
        
        # AI
        self.state = 'chase'
        self.attack_cooldown = 0
        
    def update(self, dt, player_pos, world):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        # Aim at player
        if dist > 0:
            target_angle = math.degrees(math.atan2(-dy, dx))
            angle_diff = (target_angle - self.angle + 180) % 360 - 180
            
            # Turn toward player
            if abs(angle_diff) > 5:
                self.angle += angle_diff * 2 * dt
                
            # Chase
            if dist > 100:
                self.speed += self.acceleration * dt
                self.speed = min(self.speed, self.max_speed)
            else:
                self.speed *= 0.95
                
        # Movement
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad) * dt
        self.y += self.speed * math.cos(rad) * dt
        
        # Collision with buildings
        if world:
            for building in world.buildings:
                if self.get_rect().colliderect(building['rect']):
                    self.speed *= -0.5
                    
    def get_rect(self):
        return pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        
    def draw(self, screen, camera):
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
        
        # Police lights
        light_color = (255, 0, 0) if (pygame.time.get_ticks() % 500) < 250 else (0, 0, 255)
        pygame.draw.circle(screen, light_color, (int(cx + self.width/2 * cos_a), int(cy + self.width/2 * sin_a)), 5)


class PoliceOfficer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.health = 75
        self.width = 16
        self.height = 32
        self.color = (30, 30, 100)
        
        # Combat
        self.attack_cooldown = 0
        self.damage = 15
        self.range = 200
        
        # Movement
        self.speed = 100
        
    def update(self, dt, player_pos, world):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        # Face player
        if dist > 0:
            self.angle = math.degrees(math.atan2(-dy, dx))
            
        # Move toward player
        if dist > 80:
            move_x = dx / dist * self.speed * dt
            move_y = dy / dist * self.speed * dt
            self.x += move_x
            self.y += move_y
            
        # Attack
        self.attack_cooldown -= dt
        if dist < self.range and self.attack_cooldown <= 0:
            self.attack_cooldown = 1.0
            return True  # Hit player
        return False
        
    def get_rect(self):
        return pygame.Rect(self.x - self.width/2, self.y - self.height/2, self.width, self.height)
        
    def draw(self, screen, camera):
        cx = self.x - camera.x
        cy = self.y - camera.y
        
        # Body
        pygame.draw.rect(screen, self.color, (cx - self.width//2, cy - self.height//2, self.width, self.height))
        
        # Head
        pygame.draw.circle(screen, (200, 150, 100), (int(cx), int(cy - self.height//2)), 8)
        
        # Police hat
        pygame.draw.rect(screen, (20, 20, 80), (cx - 8, cy - self.height//2 - 5, 16, 5))
        
        # Direction
        rad = math.radians(self.angle)
        end_x = cx + 15 * math.cos(rad)
        end_y = cy - 15 * math.sin(rad)
        pygame.draw.line(screen, (255, 255, 0), (cx, cy), (end_x, end_y), 2)