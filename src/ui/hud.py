import pygame
import config


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.mini_map_size = (200, 150)
        self.mini_map_margin = 10
        # temporary messages queue
        self.temp_messages = []  # each entry: {main, sub, color, timer}

    def update(self, dt):
        # decrement timers and remove expired messages
        for msg in self.temp_messages:
            msg['timer'] -= dt
        self.temp_messages = [m for m in self.temp_messages if m['timer'] > 0]

    def show_temporary_message(self, main, sub='', color=(255, 255, 255), duration=3.0):
        """Add a message that will disappear after duration seconds."""
        self.temp_messages.append({
            'main': main,
            'sub': sub,
            'color': color,
            'timer': duration
        })
        
    def format_money(self, amount):
        """Format currency with thousands separated by spaces."""
        try:
            amt = int(amount)
        except Exception:
            amt = 0
        formatted = f"{amt:,}".replace(',', ' ')
        return f"{config.CURRENCY_SYMBOL} {formatted}"

    def draw(self, screen, game):
        # draw any temporary messages first (centered)
        if self.temp_messages:
            y0 = 50
            for msg in self.temp_messages:
                main_surf = self.font.render(msg['main'], True, msg['color'])
                screen.blit(main_surf, (config.WIDTH//2 - main_surf.get_width()//2, y0))
                if msg['sub']:
                    sub_surf = self.small_font.render(msg['sub'], True, config.COLORS['WHITE'])
                    screen.blit(sub_surf, (config.WIDTH//2 - sub_surf.get_width()//2, y0 + 40))
                y0 += 80

        # Money display
        if hasattr(game, 'money'):
            money_text = self.format_money(getattr(game, 'money', 0))
            screen.blit(self.small_font.render(money_text, True, config.COLORS['WHITE']), (10, 10))

        # Wanted level display
        if hasattr(game, 'wanted_level'):
            wanted = getattr(game, 'wanted_level', 0)
            if wanted > 0:
                wanted_text = 'WANTED: ' + '★' * wanted
                screen.blit(self.small_font.render(wanted_text, True, config.COLORS['RED']), (10, 40))

        # Weapon and ammo display
        if getattr(game, 'player', None):
            weapon_key = None
            if hasattr(game.player, 'weapons') and hasattr(game.player, 'current_weapon'):
                try:
                    weapon_key = game.player.weapons[game.player.current_weapon]
                except Exception:
                    weapon_key = None

            if weapon_key:
                weapon = config.WEAPONS.get(weapon_key, {})
                icon = weapon.get('icon', '')
                ammo = game.player.ammo.get(weapon_key, 0)
                ammo_text = f"{icon} {weapon.get('name', weapon_key)} ({ammo})"
                screen.blit(self.small_font.render(ammo_text, True, config.COLORS['WHITE']), (10, 70))

        # Speedometer (only in vehicle)
        if getattr(game, 'player', None) and not game.player.is_on_foot and getattr(game, 'car', None):
            speed = abs(game.car.speed)
            screen.blit(self.small_font.render(f'Speed: {int(speed)}', True, config.COLORS['WHITE']), (10, 100))

        # In-game time display
        if getattr(game, 'time_system', None):
            game.time_system.draw_time(screen, self.small_font)
        
        # Mission / briefing text
        if getattr(game, 'mission_manager', None):
            msg = game.mission_manager.get_display_text()
            if msg:
                y = 90
                for line in msg.split('\n'):
                    surf = self.small_font.render(line, True, config.COLORS['WHITE'])
                    screen.blit(surf, (10, y))
                    y += 28

        # Interact hint text (e.g., ammo shop)
        if getattr(game, 'interact_text', None):
            hint_surf = self.small_font.render(game.interact_text, True, config.COLORS['YELLOW'])
            screen.blit(hint_surf, (10, config.HEIGHT - 60))

        # Exit confirmation prompt
        if getattr(game, 'exit_confirm', False):
            confirm = self.font.render('Exit game? Unsaved progress will be lost. (Y/N)', True, (255, 0, 0))
            screen.blit(confirm, (config.WIDTH // 2 - confirm.get_width() // 2, config.HEIGHT - 60))

        # Mini-map
        if getattr(game, 'world', None) and getattr(game, 'player', None):
            self.draw_minimap(screen, game)

        # Debug overlay (fps only) if enabled in settings
        if getattr(game, 'settings_menu', None):
            gs = game.settings_menu.graphics_settings
            if gs.get('show_overlay'):
                fps = int(game.clock.get_fps()) if hasattr(game, 'clock') else 0
                overlay_text = f"FPS: {fps}"
                text_surf = self.small_font.render(overlay_text, True, (255, 255, 0))
                pos = gs.get('overlay_position', 0)
                # map position index to coordinates
                positions = {
                    0: (10, 10),
                    1: (config.WIDTH//2 - text_surf.get_width()//2, 10),
                    2: (config.WIDTH - text_surf.get_width() - 10, 10),
                    3: (config.WIDTH - text_surf.get_width() - 10, config.HEIGHT//2 - 10),
                    4: (10, config.HEIGHT - 30),
                    5: (config.WIDTH//2 - text_surf.get_width()//2, config.HEIGHT - 30),
                    6: (config.WIDTH - text_surf.get_width() - 10, config.HEIGHT - 30),
                }
                screen.blit(text_surf, positions.get(pos, (10,10)))

    def draw_minimap(self, screen, game):
        # Small map in the top left corner
        width, height = self.mini_map_size
        x = self.mini_map_margin
        y = self.mini_map_margin

        pygame.draw.rect(screen, (10, 10, 25), (x, y, width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)

        scale = min((width - 20) / config.WORLD_SIZE, (height - 20) / config.WORLD_SIZE)
        offset_x = x + 10
        offset_y = y + 10

        # Draw roads (simplified)
        for road in game.world.roads:
            rx = offset_x + road['rect'].x * scale
            ry = offset_y + road['rect'].y * scale
            rw = max(1, road['rect'].width * scale)
            rh = max(1, road['rect'].height * scale)
            pygame.draw.rect(screen, (60, 60, 60), (rx, ry, rw, rh))

        # Draw fixed POIs
        poi_colors = {
            'safe_house': (0, 255, 0),
            'gang_house': (128, 0, 128),
            'ammo_store': (255, 0, 0),
        }
        for key, coord in config.LOCATIONS.items():
            if coord:
                px = offset_x + coord[0] * scale
                py = offset_y + coord[1] * scale
                color = poi_colors.get(key, (255, 255, 255))
                pygame.draw.circle(screen, color, (int(px), int(py)), 5)

        # Draw waypoint if set
        if hasattr(game, 'waypoint') and game.waypoint:
            wx = offset_x + game.waypoint[0] * scale
            wy = offset_y + game.waypoint[1] * scale
            # Draw waypoint radius
            pygame.draw.circle(screen, (255, 255, 0), (int(wx), int(wy)), 30, 1)
            # Draw waypoint marker
            pygame.draw.circle(screen, (255, 255, 0), (int(wx), int(wy)), 5, 1)
            # Draw line from player to waypoint
            px = offset_x + game.player.x * scale
            py = offset_y + game.player.y * scale
            pygame.draw.aaline(screen, (255, 255, 0), (int(px), int(py)), (int(wx), int(wy)))

        # Draw player
        px = offset_x + game.player.x * scale
        py = offset_y + game.player.y * scale
        pygame.draw.circle(screen, (255, 255, 0), (int(px), int(py)), 4)

        # Draw mission target
        if getattr(game, 'mission_manager', None):
            mission = game.mission_manager.get_current_mission()
            if mission and mission.get('target'):
                tx = offset_x + mission['target'][0] * scale
                ty = offset_y + mission['target'][1] * scale
                pygame.draw.circle(screen, (255, 0, 0), (int(tx), int(ty)), 5, 1)