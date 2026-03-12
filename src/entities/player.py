import pygame
import math
import config

class Player:
    def __init__(self, x=200, y=200, sound_manager=None):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 0.0
        self.is_on_foot = True
        self.health = config.PLAYER_CONFIG['health']
        self.max_health = config.PLAYER_CONFIG['health']
        self.sound_manager = sound_manager
        
        # Movement
        self.walking_speed = config.PLAYER_CONFIG['walking_speed']
        self.running_speed = config.PLAYER_CONFIG['running_speed']
        
        # Visual
        self.width = config.PLAYER_CONFIG['width']
        self.height = config.PLAYER_CONFIG['height']
        self.color = (100, 150, 255)
        
        # Weapons
        self.weapons = ['fists', 'pistol', 'machine_gun', 'grenade']
        self.current_weapon = 0
        self.ammo = {
            'pistol': 48,
            'machine_gun': 90,
            'shotgun': 24,
            'grenade': 10,
            'rifle': 60,
        }
        
        # Attack
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_hit = False
        
        # Aiming
        self.is_aiming = False
        self.aim_angle = 0
        
    def update(self, dt, keys, mouse_pos, mouse_buttons):
        if self.is_on_foot:
            self.update_on_foot(dt, keys, mouse_pos, mouse_buttons)
        else:
            self.update_in_vehicle(dt, keys)
            
    def update_on_foot(self, dt, keys, mouse_pos, mouse_buttons):
        # Movement
        move_x = 0
        move_y = 0
        
        # Check if running
        is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = self.running_speed if is_running else self.walking_speed
        
        if keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_s]:
            move_y += 1
        if keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_d]:
            move_x += 1
            
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707
            move_y *= 0.707
            
        # Apply movement
        self.x += move_x * current_speed * dt
        self.y += move_y * current_speed * dt
        
        # Rotation toward mouse
        if mouse_pos:
            screen_x = self.x - camera.x if hasattr(self, 'x') else 0
            screen_y = self.y - camera.y if hasattr(self, 'y') else 0
            dx = mouse_pos[0] - screen_x
            dy = mouse_pos[1] - screen_y
            self.angle = math.degrees(math.atan2(-dy, dx))
            
        # Attack
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        if mouse_buttons[0] and self.attack_cooldown <= 0:
            self.attack()
            
        # Grenade throw (G key)
        if keys[pygame.K_g] and self.attack_cooldown <= 0:
            if self.ammo.get('grenade', 0) > 0:
                self.current_weapon = self.weapons.index('grenade') if 'grenade' in self.weapons else 0
                self.attack()
                
        # Weapon cycling
        if keys[pygame.K_q]:
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
            
        # Number keys for weapon selection
        for i in range(1, 6):
            if keys[getattr(pygame, f'K_{i}', pygame.K_1)]:
                if i - 1 < len(self.weapons):
                    self.current_weapon = i - 1
                    
    def update_in_vehicle(self, dt, keys):
        # Vehicle controls handled by car
        pass
        
    def attack(self):
        weapon = config.WEAPONS[self.weapons[self.current_weapon]]
        
        if not weapon.get('infinite', False):
            ammo_key = self.weapons[self.current_weapon]
            if self.ammo.get(ammo_key, 0) <= 0:
                return
            self.ammo[ammo_key] -= 1
            
        self.is_attacking = True
        self.attack_timer = weapon['cooldown']
        self.attack_cooldown = weapon['cooldown']
        self.attack_hit = True

        # Play weapon sound if available
        if getattr(self, 'sound_manager', None):
            # Use weapon key as sound key (e.g. 'pistol', 'shotgun')
            sound_key = self.weapons[self.current_weapon]
            self.sound_manager.play_sfx(sound_key)
        
    def get_weapon(self):
        if self.current_weapon < len(self.weapons):
            return config.WEAPONS[self.weapons[self.current_weapon]]
        return config.WEAPONS['fists']
        
    def get_attack_point(self):
        weapon = self.get_weapon()
        rad = math.radians(self.angle)
        range_val = weapon['range']
        
        # Offset attack point to right side
        offset_x = 10 * math.cos(rad)
        offset_y = -10 * math.sin(rad)
        
        return (
            self.x + offset_x + range_val * math.cos(rad),
            self.y + offset_y - range_val * math.sin(rad)
        )
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            
    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
            
    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        
    def draw(self, screen, camera):
        # Draw player as a simple shape
        cx = self.x - camera.x
        cy = self.y - camera.y
        
        # Body
        pygame.draw.rect(screen, self.color, 
                        (cx - self.width//2, cy - self.height//2, 
                         self.width, self.height))
        
        # Direction indicator
        rad = math.radians(self.angle)
        end_x = cx + 20 * math.cos(rad)
        end_y = cy - 20 * math.sin(rad)
        pygame.draw.line(screen, (255, 255, 0), (cx, cy), (end_x, end_y), 2)
        
        # Weapon indicator
        weapon = self.get_weapon()
        if weapon:
            # Show range indicator when a ranged weapon is equipped (not fists)
            if not weapon.get('infinite', False):
                pygame.draw.circle(screen, (255, 0, 0), (int(end_x), int(end_y)), 
                                 int(weapon['range']), 1)
            # Draw attack range circle when attacking
            if self.is_attacking and self.attack_timer > 0 and not weapon.get('infinite', False):
                pygame.draw.circle(screen, (255, 255, 0), (int(end_x), int(end_y)), 
                                 int(weapon['range']), 2)

    def enter_vehicle(self, vehicle):
        self.is_on_foot = False
        vehicle.driver = self
        
    def exit_vehicle(self):
        self.is_on_foot = True
        # Offset player from car
        rad = math.radians(self.angle + 90)
        self.x = self.x + 50 * math.cos(rad)
        self.y = self.y + 50 * math.sin(rad)


# Global camera reference for player rotation
camera = None

def set_camera(cam):
    global camera
    camera = cam

