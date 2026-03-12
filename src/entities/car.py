import pygame
import math
import config

class Car:
    def __init__(self, car_type='default', x=200, y=200):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 0.0
        self.car_type = car_type
        
        # Get car configuration (allow passing either a key or a config dict)
        if isinstance(car_type, dict):
            self.config = car_type
            self.car_type = car_type.get('name', 'default')
        else:
            self.config = config.CAR_CONFIG.get(car_type, config.CAR_CONFIG['default'])
        
        # Physics properties
        self.acceleration = self.config['acceleration']
        self.drag = self.config['drag']
        self.turn_speed = self.config['turn_speed']
        self.max_speed = self.config['max_speed']
        self.weight = self.config['weight']
        
        # Visual properties
        self.color = self.config['color']
        self.width = self.config['width']
        self.height = self.config['height']
        self.name = self.config['name']
        
        # Vehicle state
        self.driver = None
        self.passengers = []
        self.health = 100
        self.max_health = 100
        self.is_locked = False
        self.is_damaged = False
        
        # Effects
        self.horn_timer = 0
        
    def update(self, dt, keys):
        if self.driver is not None:
            self.update_driving(dt, keys)
        else:
            # Slow down when no driver
            self.speed *= math.exp(-self.drag * dt * 2)
            
    def update_driving(self, dt, keys):
        # Input handling
        accel_input = 0
        turn_input = 0
        
        if keys[pygame.K_w]:
            accel_input = 1
        if keys[pygame.K_s]:
            accel_input = -0.5
        if keys[pygame.K_a]:
            turn_input = 1
        if keys[pygame.K_d]:
            turn_input = -1
            
        # Apply physics
        self.speed += accel_input * self.acceleration * dt
        self.speed = max(-self.max_speed * 0.5, min(self.speed, self.max_speed))
        self.speed *= math.exp(-self.drag * dt)
        
        # Turning (only when moving)
        if abs(self.speed) > 10:
            turn_strength = (abs(self.speed) / self.max_speed) * self.turn_speed
            # Reverse steering when going backwards
            direction = 1 if self.speed > 0 else -1
            self.angle += turn_input * turn_strength * dt * direction
            
        # Movement
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad) * dt
        self.y += self.speed * math.cos(rad) * dt
        
        # Horn
        if keys[pygame.K_h] and self.horn_timer <= 0:
            self.horn_timer = 0.3
            return True  # Horn pressed
            
        self.horn_timer -= dt
        
        return False
        
    def honk(self):
        return True  # Play horn sound
        
    def get_rect(self):
        return pygame.Rect(self.x - self.width/2, 
                          self.y - self.height/2, 
                          self.width, self.height)
    
    def draw(self, screen, camera, is_night=False):
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
            
        # Car body
        pygame.draw.polygon(screen, self.color, rotated_points)
        
        # Windshield (darker)
        windshield_points = []
        for px, py in [(-self.width/3, -self.height/3), (self.width/3, -self.height/3),
                       (self.width/4, 0), (-self.width/4, 0)]:
            rx = px * cos_a - py * sin_a + cx
            ry = px * sin_a + py * cos_a + cy
            windshield_points.append((rx, ry))
        pygame.draw.polygon(screen, (50, 50, 70), windshield_points)
        
        # Headlights at night
        if is_night:
            # Front lights
            rad = math.radians(self.angle)
            light_x = cx + self.width/2 * cos_a
            light_y = cy + self.width/2 * sin_a
            
            # Draw headlight beams
            for offset in [-self.height/3, self.height/3]:
                beam_start_x = cx + (self.width/2 + 2) * cos_a - offset * sin_a
                beam_start_y = cy + (self.width/2 + 2) * sin_a + offset * cos_a
                
                beam_end_x = beam_start_x + 60 * math.cos(rad)
                beam_end_y = beam_start_y - 60 * math.sin(rad)
                
                pygame.draw.line(screen, (255, 255, 200), 
                               (beam_start_x, beam_start_y), 
                               (beam_end_x, beam_end_y), 3)
        
        # Direction line (headlights indicator in day)
        dx = 25 * sin_a + cx
        dy = 25 * cos_a + cy
        pygame.draw.line(screen, (255, 255, 0), (cx, cy), (dx, dy), 2)
        
        # Damage indicator
        if self.is_damaged:
            pygame.draw.polygon(screen, (100, 0, 0), rotated_points, 3)
            
        # Health bar (if damaged)
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
                            
    def take_damage(self, amount):
        self.health -= amount
        if self.health < self.max_health:
            self.is_damaged = True
        return self.health <= 0
        
    def repair(self, amount):
        self.health += amount
        if self.health >= self.max_health:
            self.health = self.max_health
            self.is_damaged = False


class VehicleManager:
    def __init__(self):
        self.vehicles = []
        self.nearby_vehicles = []
        
    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        
    def spawn_random_vehicles(self, count, world_size, buildings):
        import random
        
        for _ in range(count):
            # Find a spawn position not inside a building
            valid = False
            attempts = 0
            while not valid and attempts < 50:
                x = random.randint(200, world_size - 200)
                y = random.randint(200, world_size - 200)
                
                # Check if not in building
                in_building = False
                for b in buildings:
                    if b.collidepoint(x, y):
                        in_building = True
                        break
                        
                if not in_building:
                    valid = True
                    
                attempts += 1
                
            if valid:
                car_types = list(config.CAR_CONFIG.keys())
                car_type = random.choice(car_types)
                vehicle = Car(car_type, x, y)
                self.add_vehicle(vehicle)
                
    def find_nearest_vehicle(self, x, y, max_dist=100):
        nearest = None
        min_dist = max_dist
        
        for v in self.vehicles:
            dist = math.hypot(v.x - x, v.y - y)
            if dist < min_dist:
                min_dist = dist
                nearest = v
                
        return nearest
        
    def update(self, dt, keys):
        for v in self.vehicles:
            v.update(dt, keys)
            
    def draw(self, screen, camera, is_night=False):
        for v in self.vehicles:
            v.draw(screen, camera, is_night)
            
    def get_vehicles_in_view(self, camera):
        view_rect = pygame.Rect(camera.x, camera.y, camera.width, camera.height)
        return [v for v in self.vehicles if v.get_rect().colliderect(view_rect)]

