import pygame
import math
import config

class Bullet:
    def __init__(self, x, y, angle, weapon_type, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.weapon_type = weapon_type
        self.owner = owner  # 'player' or 'enemy'
        
        weapon = config.WEAPONS[weapon_type]
        self.speed = 800 if weapon_type != 'grenade' else 200
        self.damage = weapon['damage']
        self.range = weapon['range']
        self.radius = 3 if weapon_type != 'grenade' else 8
        
        # For grenades
        self.explosion_radius = weapon.get('explosion_radius', 0)
        
        self.distance_traveled = 0
        self.active = True
        self.is_grenade = weapon_type == 'grenade'
        self.grenade_timer = 2.0  # 2 seconds before explosion
        
    def update(self, dt):
        if self.is_grenade:
            self.grenade_timer -= dt
            if self.grenade_timer <= 0:
                self.explode()
            return
            
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed * dt
        dy = -math.sin(rad) * self.speed * dt
        
        self.x += dx
        self.y += dy
        self.distance_traveled += math.hypot(dx, dy)
        
        if self.distance_traveled >= self.range:
            self.active = False
            
    def explode(self):
        self.active = False
        # Return explosion info for damage calculation
        return {
            'x': self.x,
            'y': self.y,
            'radius': self.explosion_radius,
            'damage': self.damage
        }
        
    def draw(self, screen, camera):
        cx = self.x - camera.x
        cy = self.y - camera.y
        
        if self.is_grenade:
            # Draw grenade with pulsing effect
            color = (255, 100, 0) if self.grenade_timer < 0.5 else (50, 200, 50)
            pygame.draw.circle(screen, color, (int(cx), int(cy)), self.radius)
            # Fuse spark
            pygame.draw.circle(screen, (255, 255, 0), (int(cx), int(cy - 5)), 2)
        else:
            color = (255, 255, 0) if self.owner == 'player' else (255, 0, 0)
            pygame.draw.circle(screen, color, (int(cx), int(cy)), self.radius)


class Grenade:
    def __init__(self, x, y, angle, thrower):
        self.x = x
        self.y = y
        self.angle = angle
        self.thrower = thrower
        
        weapon = config.WEAPONS['grenade']
        self.speed = 300
        self.explosion_radius = weapon['explosion_radius']
        self.damage = weapon['damage']
        
        # Initial velocity (throw arc)
        rad = math.radians(angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = -math.sin(rad) * self.speed
        
        self.timer = 2.0  # 2 seconds
        self.active = True
        self.exploded = False
        
    def update(self, dt):
        if not self.active:
            return
            
        self.timer -= dt
        
        # Arc motion
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 400 * dt  # Gravity
        
        # Bounce off ground
        if self.y > 3500:  # Ground level
            self.y = 3500
            self.vy *= -0.5
            
        if self.timer <= 0:
            self.explode()
            
    def explode(self):
        self.active = False
        self.exploded = True
        
    def get_explosion_info(self):
        return {
            'x': self.x,
            'y': self.y,
            'radius': self.explosion_radius,
            'damage': self.damage
        }
        
    def draw(self, screen, camera):
        if not self.active:
            return
            
        cx = self.x - camera.x
        cy = self.y - camera.y
        
        # Grenade body
        color = (50, 200, 50) if self.timer > 0.5 else (255, 100, 0)
        pygame.draw.circle(screen, color, (int(cx), int(cy)), 8)
        
        # Fuse
        if self.timer < 1.0:
            pygame.draw.circle(screen, (255, 255, 0), (int(cx), int(cy - 8)), 3)
            
        # Explosion radius preview when about to explode
        if self.timer < 0.3:
            pygame.draw.circle(screen, (255, 100, 0), (int(cx), int(cy)), 
                             int(self.explosion_radius), 1)


class WeaponPickup:
    def __init__(self, x, y, weapon_type):
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
        self.width = 20
        self.height = 20
        self.active = True
        
        weapon = config.WEAPONS[weapon_type]
        self.ammo = weapon.get('ammo', 20) * 2
        
    def draw(self, screen, camera):
        if not self.active:
            return
            
        cx = self.x - camera.x
        cy = self.y - camera.y
        
        # Draw pickup marker
        pygame.draw.rect(screen, (100, 100, 100), 
                        (cx - 10, cy - 10, 20, 20))
        pygame.draw.rect(screen, (255, 255, 0), 
                        (cx - 10, cy - 10, 20, 20), 2)
                        
        # Weapon icon (letter)
        font = pygame.font.Font(None, 20)
        text = font.render(self.weapon_type[0].upper(), True, (255, 255, 0))
        screen.blit(text, (cx - 6, cy - 8))
        
    def get_rect(self):
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

