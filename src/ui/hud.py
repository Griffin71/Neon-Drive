import pygame
import math
import random
import config
from typing import List, Dict, Any, Optional, Tuple

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.mini_map_size = (200, 150)
        self.mini_map_margin = 10
        
        # Temporary messages
        self.temp_messages: List[Dict[str, Any]] = []
        self.message_animations = {}
        self.next_message_id = 0
        
        # Effects
        self.damage_flash_timer = 0
        self.screen_shake = 0
        
        # UI panel backgrounds
        self.panel_bg_alpha = 180
        
        # Compass directions
        self.directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        
        # Weapon wheel
        self.weapon_wheel_open = False
        self.radio_wheel_open = False
        
    def update(self, dt: float):
        # Update message timers
        for msg in self.temp_messages:
            msg['timer'] -= dt
        self.temp_messages = [m for m in self.temp_messages if m['timer'] > 0]
        
        # Update animations
        for msg_id in list(self.message_animations.keys()):
            self.message_animations[msg_id]['timer'] -= dt
            if self.message_animations[msg_id]['timer'] <= 0:
                del self.message_animations[msg_id]
                
        # Update damage flash
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt
            
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= dt * 2
            
    def show_temporary_message(self, main: str, sub: str = '', color: Tuple[int, int, int] = (255, 255, 255), 
                               duration: float = 3.0, icon: Optional[str] = None):
        msg_id = self.next_message_id
        self.next_message_id += 1
        
        self.temp_messages.append({
            'id': msg_id, 'main': main, 'sub': sub, 'color': color, 
            'timer': duration, 'icon': icon
        })
        self.message_animations[msg_id] = {'timer': 0.3, 'alpha': 0}
        
    def show_damage_flash(self):
        self.damage_flash_timer = 0.2
        
    def add_screen_shake(self, intensity: float = 5.0):
        self.screen_shake = max(self.screen_shake, intensity)
        
    def get_shake_offset(self) -> Tuple[int, int]:
        if self.screen_shake <= 0:
            return (0, 0)
        return (random.randint(-int(self.screen_shake), int(self.screen_shake)),
                random.randint(-int(self.screen_shake), int(self.screen_shake)))
                
    def format_money(self, amount) -> str:
        try:
            amt = int(amount)
        except:
            amt = 0
        return f"{config.CURRENCY_SYMBOL} {amt:,}".replace(',', ' ')
        
    def get_direction(self, angle_deg: float) -> str:
        idx = int((angle_deg + 22.5) % 360 / 45)
        return self.directions[idx]
        
    def draw_panel_background(self, screen: pygame.Surface, rect: pygame.Rect):
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill((0, 0, 0, self.panel_bg_alpha))
        screen.blit(s, rect)
        
    def draw_weapon_hud(self, screen, game, shake_x, shake_y):
        """Draw weapon info in top-right corner"""
        if not game.player:
            return
            
        # Weapon panel position (top right)
        panel_width = 200
        panel_height = 80
        panel_x = config.WIDTH - panel_width - 10
        panel_y = 10
        
        # Draw panel background
        self.draw_panel_background(screen, pygame.Rect(panel_x, panel_y, panel_width, panel_height))
        
        # Get current weapon
        weapon_key = game.player.weapons[game.player.current_weapon]
        weapon = config.WEAPONS.get(weapon_key, {})
        
        # Weapon name and icon
        icon = weapon.get('icon', '🔫')
        name = weapon.get('name', weapon_key)
        
        # Draw icon
        icon_surf = self.font.render(icon, True, (255, 255, 255))
        screen.blit(icon_surf, (panel_x + 10 + shake_x, panel_y + 15 + shake_y))
        
        # Draw name
        name_surf = self.small_font.render(name, True, (255, 255, 0))
        screen.blit(name_surf, (panel_x + 50 + shake_x, panel_y + 15 + shake_y))
        
        # Draw ammo
        if not weapon.get('infinite', False):
            ammo = game.player.ammo.get(weapon_key, 0)
            max_ammo = weapon.get('ammo', 30)
            ammo_text = f"Ammo: {ammo}/{max_ammo}"
            ammo_surf = self.small_font.render(ammo_text, True, (255, 255, 255))
            screen.blit(ammo_surf, (panel_x + 50 + shake_x, panel_y + 45 + shake_y))
            
            # Ammo bar
            bar_width = 130
            bar_height = 6
            fill_width = int((ammo / max_ammo) * bar_width)
            pygame.draw.rect(screen, (50, 50, 50), (panel_x + 50, panel_y + 60, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 200, 0), (panel_x + 50, panel_y + 60, fill_width, bar_height))
            
    def draw_time_hud(self, screen, game, shake_x, shake_y):
        """Draw time in top-left corner"""
        if not game.time_system:
            return
            
        # Time panel
        panel_width = 150
        panel_height = 50
        panel_x = 10
        panel_y = 10
        
        self.draw_panel_background(screen, pygame.Rect(panel_x, panel_y, panel_width, panel_height))
        
        # Get time string
        time_str = game.time_system.get_time_string()
        time_surf = self.small_font.render(time_str, True, (255, 255, 255))
        screen.blit(time_surf, (panel_x + 10 + shake_x, panel_y + 15 + shake_y))
        
        # Day/night indicator
        is_night = game.time_system.is_night()
        night_text = "🌙 Night" if is_night else "☀️ Day"
        night_surf = self.small_font.render(night_text, True, (200, 200, 200) if is_night else (255, 255, 100))
        screen.blit(night_surf, (panel_x + 10 + shake_x, panel_y + 35 + shake_y))
        
    def draw_minimap(self, screen, game, shake_x, shake_y):
        """Draw minimap in bottom-left corner"""
        width, height = self.mini_map_size
        x = self.mini_map_margin
        y = config.HEIGHT - height - self.mini_map_margin
        
        # Background
        pygame.draw.rect(screen, (10, 10, 25), (x + shake_x, y + shake_y, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x + shake_x, y + shake_y, width, height), 2)
        
        scale = min((width - 20) / config.WORLD_SIZE, (height - 20) / config.WORLD_SIZE)
        offset_x = x + 10 + shake_x
        offset_y = y + 10 + shake_y
        
        # Draw roads
        if game.world and hasattr(game.world, 'roads'):
            for road in game.world.roads:
                rx = offset_x + road['rect'].x * scale
                ry = offset_y + road['rect'].y * scale
                rw = max(1, road['rect'].width * scale)
                rh = max(1, road['rect'].height * scale)
                pygame.draw.rect(screen, (60, 60, 60), (rx, ry, rw, rh))
                
        # Draw buildings
        if game.world:
            for building in game.world.buildings:
                bx = offset_x + building['rect'].x * scale
                by = offset_y + building['rect'].y * scale
                bw = max(2, building['rect'].width * scale)
                bh = max(2, building['rect'].height * scale)
                pygame.draw.rect(screen, (80, 80, 80), (bx, by, bw, bh))
                
        # Draw player
        px = offset_x + game.player.x * scale
        py = offset_y + game.player.y * scale
        pygame.draw.circle(screen, (255, 255, 0), (int(px), int(py)), 5)
        
        # Draw player direction
        if hasattr(game.player, 'angle'):
            rad = math.radians(game.player.angle)
            dir_x = px + 8 * math.sin(rad)
            dir_y = py + 8 * math.cos(rad)
            pygame.draw.line(screen, (255, 255, 255), (px, py), (dir_x, dir_y), 2)
            
        # Draw enemies
        for enemy in game.enemies:
            ex = offset_x + enemy.x * scale
            ey = offset_y + enemy.y * scale
            pygame.draw.circle(screen, (255, 0, 0), (int(ex), int(ey)), 3)
            
        # Draw police
        if hasattr(game, 'police_system'):
            for vehicle in game.police_system.police_vehicles:
                vx = offset_x + vehicle.x * scale
                vy = offset_y + vehicle.y * scale
                pygame.draw.circle(screen, (0, 0, 255), (int(vx), int(vy)), 4)
                
        # Draw mission target
        if game.mission_manager and game.mission_manager.get_current_mission():
            mission = game.mission_manager.get_current_mission()
            if mission and mission.get('target'):
                tx = offset_x + mission['target'][0] * scale
                ty = offset_y + mission['target'][1] * scale
                pygame.draw.circle(screen, (255, 0, 0), (int(tx), int(ty)), 5, 1)
                
    def draw_compass(self, screen, game, shake_x, shake_y):
        """Draw compass at top center"""
        if not game.player:
            return
            
        direction = self.get_direction(game.player.angle)
        compass_text = f"▲ {direction}"
        compass_surf = self.small_font.render(compass_text, True, (200, 200, 200))
        screen.blit(compass_surf, (config.WIDTH//2 - compass_surf.get_width()//2 + shake_x, 10 + shake_y))
        
    def draw(self, screen, game):
        shake_x, shake_y = self.get_shake_offset()
        
        # Damage flash
        if self.damage_flash_timer > 0:
            flash_alpha = int(255 * (self.damage_flash_timer / 0.2))
            flash_surface = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, flash_alpha))
            screen.blit(flash_surface, (0, 0))
            
        # Temporary messages
        if self.temp_messages:
            y0 = 50
            for msg in self.temp_messages:
                anim = self.message_animations.get(msg['id'], {'alpha': 255})
                alpha = min(255, int(anim.get('alpha', 255) * 255))
                
                main_surf = self.font.render(msg['main'], True, msg['color'])
                main_surf.set_alpha(alpha)
                screen.blit(main_surf, (config.WIDTH//2 - main_surf.get_width()//2 + shake_x, y0 + shake_y))
                
                if msg['sub']:
                    sub_surf = self.small_font.render(msg['sub'], True, (255, 255, 255))
                    sub_surf.set_alpha(alpha)
                    screen.blit(sub_surf, (config.WIDTH//2 - sub_surf.get_width()//2 + shake_x, y0 + 40 + shake_y))
                y0 += 80
                
        # Draw UI panels
        self.draw_weapon_hud(screen, game, shake_x, shake_y)
        self.draw_time_hud(screen, game, shake_x, shake_y)
        self.draw_compass(screen, game, shake_x, shake_y)
        self.draw_minimap(screen, game, shake_x, shake_y)
        
        # Health bar (bottom center)
        if game.player:
            health_percent = game.player.health / game.player.max_health
            bar_width = 300
            bar_height = 20
            bar_x = config.WIDTH//2 - bar_width//2
            bar_y = config.HEIGHT - 40
            
            # Health bar background
            pygame.draw.rect(screen, (50, 50, 50), (bar_x + shake_x, bar_y + shake_y, bar_width, bar_height))
            
            # Health fill
            if health_percent > 0.6:
                color = (0, 255, 0)
            elif health_percent > 0.3:
                color = (255, 255, 0)
            else:
                color = (255, 0, 0)
                # Flash when low
                if pygame.time.get_ticks() % 500 < 250:
                    color = (255, 100, 100)
                    
            fill_width = int(bar_width * health_percent)
            pygame.draw.rect(screen, color, (bar_x + shake_x, bar_y + shake_y, fill_width, bar_height))
            
            # Health text
            health_text = f"HEALTH: {int(game.player.health)}/{game.player.max_health}"
            health_surf = self.small_font.render(health_text, True, (255, 255, 255))
            screen.blit(health_surf, (bar_x + bar_width//2 - health_surf.get_width()//2 + shake_x, bar_y - 20 + shake_y))
            
        # Speedometer (when in vehicle)
        if game.car and game.player and not game.player.is_on_foot:
            speed = abs(game.car.speed)
            speed_text = f"SPEED: {int(speed)}"
            speed_surf = self.small_font.render(speed_text, True, (255, 255, 255))
            screen.blit(speed_surf, (config.WIDTH - 150 + shake_x, config.HEIGHT - 80 + shake_y))
            
        # Wanted level (top right below weapon)
        if game.wanted_level > 0:
            wanted_text = "WANTED: " + "★" * game.wanted_level
            wanted_surf = self.small_font.render(wanted_text, True, (255, 0, 0))
            screen.blit(wanted_surf, (config.WIDTH - wanted_surf.get_width() - 10 + shake_x, 100 + shake_y))
            
        # Mission text (left side)
        if game.mission_manager:
            mission_text = game.mission_manager.get_display_text()
            if mission_text:
                lines = mission_text.split('\n')
                y = config.HEIGHT - 150
                for i, line in enumerate(lines):
                    # Highlight objectives
                    if "Objective" in line or "MISSION" in line:
                        color = (255, 255, 0)
                    elif "Press SPACE" in line:
                        color = (0, 255, 255)
                    else:
                        color = (255, 255, 255)
                    surf = self.small_font.render(line, True, color)
                    screen.blit(surf, (10 + shake_x, y + i * 25 + shake_y))