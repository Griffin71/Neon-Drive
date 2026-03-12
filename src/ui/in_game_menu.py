import pygame
import config

class InGameMenu:
    def __init__(self, save_system, sound_manager=None):
        self.save_system = save_system
        self.sound_manager = sound_manager
        self.font_title = pygame.font.Font(None, 48)
        self.font_menu = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Tab options (Map shown first)
        self.tabs = ['Map', 'Stats', 'Inventory', 'Settings', 'Save Game', 'Exit']
        self.selected_tab = 0
        
        # Map state
        self.map_zoom = 1.0
        self.map_offset = (0, 0)

        # Save selection
        self.save_slot = 1

        # Exit confirmation
        self.exit_confirm = False

        # Save game selection
        self.save_slot = 1
        
    def handle_event(self, event, game):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
                # Cancel exit prompt if open
                if self.exit_confirm:
                    self.exit_confirm = False
                    return None
                return 'close'
            elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                if self.sound_manager:
                    self.sound_manager.play_sfx('button_scroll')

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_tab = max(0, self.selected_tab - 1)
                else:
                    self.selected_tab = min(len(self.tabs) - 1, self.selected_tab + 1)
            elif event.key == pygame.K_1:
                if self.tabs[self.selected_tab] == 'Save Game':
                    self.save_slot = 1
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                else:
                    self.selected_tab = 0
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_2:
                if self.tabs[self.selected_tab] == 'Save Game':
                    self.save_slot = 2
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                else:
                    self.selected_tab = 1
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_3:
                if self.tabs[self.selected_tab] == 'Save Game':
                    self.save_slot = 3
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                else:
                    self.selected_tab = 2
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_4:
                if self.tabs[self.selected_tab] == 'Save Game':
                    self.save_slot = 4
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                else:
                    self.selected_tab = 3
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_5:
                if self.tabs[self.selected_tab] == 'Save Game':
                    self.save_slot = 5
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                else:
                    self.selected_tab = 4
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_6:
                if self.tabs[self.selected_tab] == 'Save Game':
                    self.save_slot = 6
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                else:
                    self.selected_tab = 5
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_7 and self.tabs[self.selected_tab] == 'Save Game':
                self.save_slot = 7
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_8 and self.tabs[self.selected_tab] == 'Save Game':
                self.save_slot = 8
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_9 and self.tabs[self.selected_tab] == 'Save Game':
                self.save_slot = 9
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_0 and self.tabs[self.selected_tab] == 'Save Game':
                self.save_slot = 10
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_RETURN:
                if self.tabs[self.selected_tab] == 'Exit':
                    return 'exit'
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # tab click detection
            tab_width = 180
            start_x = (config.WIDTH - len(self.tabs) * tab_width) // 2
            y = 20
            for i, tab in enumerate(self.tabs):
                rect = pygame.Rect(start_x + i * tab_width, y, tab_width - 5, 40)
                if rect.collidepoint(mx, my):
                    self.selected_tab = i
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                    return None
            # save slot clicks
            if self.tabs[self.selected_tab] == 'Save Game':
                base_y = 160
                slot_h = 35
                for slot in range(1, 11):
                    y_pos = base_y + (slot - 1) * slot_h
                    # we draw slots centered; approximate clickable rect
                    text_w = 300
                    x_pos = config.WIDTH//2 - text_w//2
                    rect = pygame.Rect(x_pos, y_pos, text_w, slot_h)
                    if rect.collidepoint(mx, my):
                        self.save_slot = slot
                        if self.sound_manager:
                            self.sound_manager.play_sfx('opt_clicked')
                        return None
        # Waypoint setting via mouse click on map
        if event.type == pygame.MOUSEBUTTONDOWN and self.tabs[self.selected_tab] == 'Map':
            if event.button == 1:  # Left click to set waypoint
                mx, my = event.pos
                map_width = 600
                map_height = 450
                map_x = (config.WIDTH - map_width) // 2
                map_y = 100

                if map_x <= mx <= map_x + map_width and map_y <= my <= map_y + map_height:
                    # Translate screen click to world coords
                    scale = (map_width - 40) / config.WORLD_SIZE
                    world_x = (mx - map_x - 20) / scale
                    world_y = (my - map_y - 20) / scale
                    if hasattr(game, 'waypoint'):
                        game.waypoint = (world_x, world_y)
                        if self.sound_manager:
                            self.sound_manager.play_sfx('opt_clicked')
            elif event.button == 3:  # Right click to clear waypoint
                if hasattr(game, 'waypoint'):
                    game.waypoint = None
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')

        return None

        # Waypoint setting via mouse click on map
        if event.type == pygame.MOUSEBUTTONDOWN and self.tabs[self.selected_tab] == 'Map':
            if event.button == 1:  # Left click to set waypoint
                mx, my = event.pos
                map_width = 600
                map_height = 450
                map_x = (config.WIDTH - map_width) // 2
                map_y = 100

                if map_x <= mx <= map_x + map_width and map_y <= my <= map_y + map_height:
                    # Translate screen click to world coords
                    scale = (map_width - 40) / config.WORLD_SIZE
                    world_x = (mx - map_x - 20) / scale
                    world_y = (my - map_y - 20) / scale
                    if hasattr(game, 'waypoint'):
                        game.waypoint = (world_x, world_y)
                        if self.sound_manager:
                            self.sound_manager.play_sfx('opt_clicked')
            elif event.button == 3:  # Right click to clear waypoint
                if hasattr(game, 'waypoint'):
                    game.waypoint = None
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')

        return None
        
    def draw(self, screen, game):
        # Semi-transparent background
        bg = pygame.Surface((config.WIDTH, config.HEIGHT))
        bg.set_alpha(200)
        bg.fill((0, 0, 0))
        screen.blit(bg, (0, 0))
        
        # Draw tabs at top
        self.draw_tabs(screen)
        
        # Draw content based on selected tab
        if self.tabs[self.selected_tab] == 'Map':
            self.draw_map(screen, game)
        elif self.tabs[self.selected_tab] == 'Stats':
            self.draw_stats(screen, game)
        elif self.tabs[self.selected_tab] == 'Inventory':
            self.draw_inventory(screen, game)
        elif self.tabs[self.selected_tab] == 'Settings':
            self.draw_settings_tab(screen, game)
        elif self.tabs[self.selected_tab] == 'Save Game':
            self.draw_save_game(screen, game)
            
        # Hint
        hint = self.font_small.render("← → or 1-5: Switch Tab  |  ESC: Close", True, (150, 150, 150))
        screen.blit(hint, (config.WIDTH // 2 - hint.get_width() // 2, config.HEIGHT - 40))

        help_text = self.font_small.render("Arrow Keys + Mouse: Navigate  |  ENTER: Select", True, (150, 150, 150))
        screen.blit(help_text, (config.WIDTH - help_text.get_width() - 20, config.HEIGHT - 40))
        
    def draw_tabs(self, screen):
        tab_width = 180
        tab_height = 40
        start_x = (config.WIDTH - len(self.tabs) * tab_width) // 2
        y = 20
        
        for i, tab in enumerate(self.tabs):
            x = start_x + i * tab_width
            
            # Background
            color = (255, 0, 128) if i == self.selected_tab else (60, 60, 80)
            pygame.draw.rect(screen, color, (x, y, tab_width - 5, tab_height))
            
            # Border
            border_color = (255, 255, 255) if i == self.selected_tab else (100, 100, 100)
            pygame.draw.rect(screen, border_color, (x, y, tab_width - 5, tab_height), 2)
            
            # Text
            text = self.font_menu.render(tab, True, (255, 255, 255))
            screen.blit(text, (x + tab_width // 2 - text.get_width() // 2, y + 8))
            
    def draw_map(self, screen, game):
        """Draw the world map - shown first as requested"""
        # Map panel
        map_width = 600
        map_height = 450
        map_x = (config.WIDTH - map_width) // 2
        map_y = 100
        
        # Map background
        pygame.draw.rect(screen, (20, 40, 20), (map_x, map_y, map_width, map_height))
        pygame.draw.rect(screen, (100, 200, 100), (map_x, map_y, map_width, map_height), 3)
        
        # Scale factor (world to map)
        scale = (map_width - 40) / config.WORLD_SIZE
        
        # Draw buildings on map
        for b in game.world.buildings:
            bx = map_x + 20 + b['rect'].x * scale
            by = map_y + 20 + b['rect'].y * scale
            bw = max(3, b['rect'].width * scale)
            bh = max(3, b['rect'].height * scale)
            pygame.draw.rect(screen, (80, 80, 80), (bx, by, bw, bh))
            
        # Draw roads on map
        for road in game.world.roads:
            rx = map_x + 20 + road['rect'].x * scale
            ry = map_y + 20 + road['rect'].y * scale
            rw = max(2, road['rect'].width * scale)
            rh = max(2, road['rect'].height * scale)
            pygame.draw.rect(screen, (60, 60, 60), (rx, ry, rw, rh))
            
        # Draw lakes on map
        for lake in game.world.lakes:
            lx = map_x + 20 + lake['rect'].x * scale
            ly = map_y + 20 + lake['rect'].y * scale
            lw = lake['rect'].width * scale
            lh = lake['rect'].height * scale
            pygame.draw.rect(screen, (30, 100, 180), (lx, ly, lw, lh))
            
        # Draw player position
        px = map_x + 20 + game.player.x * scale
        py = map_y + 20 + game.player.y * scale
        pygame.draw.circle(screen, (255, 255, 0), (int(px), int(py)), 6)

        # Draw waypoint if set
        if getattr(game, 'waypoint', None):
            wx = map_x + 20 + game.waypoint[0] * scale
            wy = map_y + 20 + game.waypoint[1] * scale
            pygame.draw.circle(screen, (255, 255, 0), (int(wx), int(wy)), 8, 2)
            pygame.draw.circle(screen, (255, 255, 0), (int(wx), int(wy)), 40, 1)

        # Draw mission target if active
        mission = game.mission_manager.get_current_mission()
        if mission and mission.get('target'):
            tx = map_x + 20 + mission['target'][0] * scale
            ty = map_y + 20 + mission['target'][1] * scale
            pygame.draw.circle(screen, (255, 0, 0), (int(tx), int(ty)), 8, 2)
            
        # Map title
        title = self.font_title.render("CITY MAP", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, map_y - 40))
        
        # Location info
        loc_text = self.font_small.render(f"Position: ({int(game.player.x)}, {int(game.player.y)})", True, (200, 200, 200))
        screen.blit(loc_text, (map_x, map_y + map_height + 10))
        
    def draw_stats(self, screen, game):
        y = 100
        
        title = self.font_title.render("PLAYER STATS", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, y))
        
        y += 60
        
        stats = [
            ("Health", f"{int(game.player.health)}/{game.player.max_health}"),
            ("Money", game.hud.format_money(getattr(game, 'money', 0))),
            ("Wanted Level", "★" * getattr(game, 'wanted_level', 0)),
            ("Current Mission", f"{game.mission_manager.current_index + 1}/{len(game.mission_manager.missions)}"),
            ("Time", game.time_system.get_time_string()),
        ]
        
        for label, value in stats:
            label_surf = self.font_menu.render(label + ":", True, (200, 200, 200))
            value_surf = self.font_menu.render(str(value), True, (255, 255, 0))
            screen.blit(label_surf, (config.WIDTH // 2 - 200, y))
            screen.blit(value_surf, (config.WIDTH // 2 + 50, y))
            y += 45
            
    def draw_inventory(self, screen, game):
        y = 100
        
        title = self.font_title.render("INVENTORY", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, y))
        
        y += 60
        
        # Weapons
        weapons_title = self.font_menu.render("Weapons:", True, (255, 0, 128))
        screen.blit(weapons_title, (config.WIDTH // 2 - 200, y))
        y += 40
        
        for i, weapon_key in enumerate(game.player.weapons):
            weapon = config.WEAPONS[weapon_key]
            selected = i == game.player.current_weapon
            color = (255, 255, 0) if selected else (255, 255, 255)
            
            ammo_text = ""
            if not weapon.get('infinite', False):
                ammo = game.player.ammo.get(weapon_key, 0)
                ammo_text = f" ({ammo})"
                
            text = f"{i+1}. {weapon['name']}{ammo_text}"
            text_surf = self.font_menu.render(text, True, color)
            screen.blit(text_surf, (config.WIDTH // 2 - 150, y))
            y += 35
            
    def draw_settings_tab(self, screen, game):
        y = 100
        
        title = self.font_title.render("IN-GAME SETTINGS", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, y))
        
        y += 60
        
        # Volume controls (simplified)
        settings = [
            ("Music Volume", "50%"),
            ("SFX Volume", "70%"),
            ("Radio Volume", "60%"),
            ("Show Mini-map", "ON"),
            ("Show HUD", "ON"),
        ]
        
        for label, value in settings:
            label_surf = self.font_menu.render(label + ":", True, (200, 200, 200))
            value_surf = self.font_menu.render(value, True, (255, 255, 0))
            screen.blit(label_surf, (config.WIDTH // 2 - 200, y))
            screen.blit(value_surf, (config.WIDTH // 2 + 100, y))
            y += 40
            
    def draw_save_game(self, screen, game):
        y = 100
        
        title = self.font_title.render("SAVE GAME", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, y))
        
        y += 60
        
        # Save slots (1-10)
        for slot in range(1, 11):
            save = self.save_system.get_save_for_slot(slot)
            selected = (slot == self.save_slot)
            color = (255, 255, 255) if selected else (180, 180, 180)
            if save:
                timestamp = save.get('timestamp', 0)
                import time
                time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp)) if timestamp else 'Unknown'
                mission = save.get('game_state', {}).get('mission', {})
                mission_index = mission.get('current_index', 0)
                mission_title = f"Mission {mission_index + 1}"
                label = f"{slot}. {save.get('name', 'Save')} ({mission_title}) - {time_str}"
            else:
                label = f"{slot}. EMPTY"

            text = self.font_menu.render(label, True, color)
            screen.blit(text, (config.WIDTH // 2 - text.get_width() // 2, y + (slot - 1) * 35))

        hint = self.font_small.render('Select slot with 1-0 keys, Press ENTER to save', True, (150, 150, 150))
        screen.blit(hint, (config.WIDTH // 2 - hint.get_width() // 2, y + 11 * 35))

