import math
import random
import pygame
from src.core.camera import Camera
from src.core.save_system import SaveSystem
from src.core.sound_manager import SoundManager
from src.entities.car import Car, VehicleManager
from src.entities.enemy import Enemy
from src.entities.player import Player, set_camera
from src.world.world import World
from src.world.time_system import TimeSystem
from src.missions.mission_manager import MissionManager
from src.ui.hud import HUD
from src.ui.main_menu import MainMenu
from src.ui.settings_menu import SettingsMenu
from src.ui.in_game_menu import InGameMenu
import config


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass

        # Start in fullscreen (actual display size)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.width, self.height = self.screen.get_size()
        config.WIDTH = self.width
        config.HEIGHT = self.height

        pygame.display.set_caption('Neon City Drive')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'intro'  # intro, menu, playing, paused, settings, load
        self.load_index = 0

        # Core systems
        self.camera = Camera(config.WIDTH, config.HEIGHT)
        set_camera(self.camera)
        self.save_system = SaveSystem()
        self.sound_manager = SoundManager()

        # Menus
        self.main_menu = MainMenu(self.save_system, self.sound_manager)
        self.settings_menu = SettingsMenu(self.sound_manager)
        self.in_game_menu = InGameMenu(self.save_system, self.sound_manager)

        # Runtime objects
        self.world = None
        self.time_system = None
        self.mission_manager = None
        self.player = None
        self.car = None
        self.vehicle_manager = VehicleManager()
        self.enemies = []
        self.hud = HUD()

        self.money = 0
        self.wanted_level = 0
        self.waypoint = None
        self.interact_text = ''

        # UI wheels
        self.radio_wheel_open = False
        self.weapon_wheel_open = False
        self.wheel_timer = 0.0

        # Input tracking
        self._f_pressed_last_frame = False
        self.exit_confirm = False

        # Intro splash
        self.intro_start = pygame.time.get_ticks()
        self.intro_duration = 5000
        self.sound_manager.play_music('final_theme_maybe', loops=0, volume=1.0)

    def start_new_game(self):
        self.world = World()
        self.time_system = TimeSystem()
        self.mission_manager = MissionManager()
        self.player = Player(x=600, y=600, sound_manager=self.sound_manager)
        self.car = Car('default', x=self.player.x + 60, y=self.player.y)

        # Populate the world with some basic enemies and vehicles
        self.spawn_enemies(10)
        self.vehicle_manager.spawn_random_vehicles(10, config.WORLD_SIZE, [b['rect'] for b in self.world.buildings])

        self.player.is_on_foot = True
        self.car.driver = None

        self.money = 0
        self.wanted_level = 0
        self.waypoint = None
        self.interact_text = ''
        self.radio_wheel_open = False
        self.weapon_wheel_open = False
        self.wheel_timer = 0.0

        self.camera.update(self.player.x, self.player.y)
        self.state = 'playing'

    def load_game(self, save_data):
        # Start a fresh game world then apply save
        self.start_new_game()
        self.waypoint = None
        self.interact_text = ''
        self.radio_wheel_open = False
        self.weapon_wheel_open = False
        self.wheel_timer = 0.0
        if save_data:
            self.save_system.load_game(save_data, self)

        # Ensure player knows about sound manager for weapon SFX
        if self.player:
            self.player.sound_manager = self.sound_manager

        self.state = 'playing'

    def respawn_player(self, penalty=1500, reason=None):
        """Respawn the player at the hospital (or safe house) and apply a cash penalty."""
        if not self.player:
            return

        # Apply penalty
        self.money = max(0, self.money - penalty)

        # Teleport to hospital or safe house
        hospital = config.LOCATIONS.get('hospital') or config.LOCATIONS.get('safe_house')
        if hospital:
            self.player.x, self.player.y = hospital
            if self.car:
                self.car.x = self.player.x + 60
                self.car.y = self.player.y
                self.car.speed = 0
                self.car.driver = None

        # Restore health
        self.player.health = self.player.max_health

        # Show message
        if self.hud:
            msg = 'You died' if not reason else reason
            self.hud.show_temporary_message(msg, f'Respawned at hospital (-{self.hud.format_money(penalty)})', (255, 50, 50), 4)

    def save_at_safehouse(self):
        """Save the game from the safe house and optionally park the car."""
        if self.save_system:
            success, _ = self.save_system.save_game(self, slot=1)
            if self.hud:
                if success:
                    self.hud.show_temporary_message('Saved at Safe House', 'Slot 1', (0, 255, 0), 3)
                else:
                    self.hud.show_temporary_message('Save failed', '', (255, 0, 0), 3)

        # Park car at safe house
        safe_loc = config.LOCATIONS.get('safe_house')
        if safe_loc and self.car:
            self.car.x = safe_loc[0] + 60
            self.car.y = safe_loc[1]
            self.car.speed = 0
            self.car.driver = self.player if not self.player.is_on_foot else None
            if self.player:
                self.player.x, self.player.y = safe_loc

    def apply_graphics_settings(self):
        """Apply current graphics settings to the display."""
        if not getattr(self, 'settings_menu', None):
            return
        gs = self.settings_menu.graphics_settings
        resolutions = config.GRAPHICS_SETTINGS.get('resolutions', [])
        res_idx = gs.get('resolution', 0)
        if 0 <= res_idx < len(resolutions):
            res = resolutions[res_idx]
        else:
            res = config.GRAPHICS_SETTINGS['default']['resolution']

        screen_types = config.GRAPHICS_SETTINGS.get('screen_types', [])
        type_idx = gs.get('screen_type', 0)
        screen_type = screen_types[type_idx] if 0 <= type_idx < len(screen_types) else config.GRAPHICS_SETTINGS['default']['screen_type']

        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if screen_type == 'fullscreen':
            flags |= pygame.FULLSCREEN
        elif screen_type == 'borderless':
            flags |= pygame.NOFRAME

        self.screen = pygame.display.set_mode(res, flags)
        self.width, self.height = self.screen.get_size()
        config.WIDTH = self.width
        config.HEIGHT = self.height
        # Update camera dimensions
        self.camera = Camera(self.width, self.height)

    def handle_player_attack(self):
        """Resolve attack hits against enemies."""
        if not self.player:
            return
        weapon_key = self.player.weapons[self.player.current_weapon]
        weapon = config.WEAPONS.get(weapon_key, {})
        damage = weapon.get('damage', 10)

        # Attack point for ranged weapons
        attack_point = self.player.get_attack_point()
        for enemy in list(self.enemies):
            if enemy.health <= 0:
                continue
            dx = enemy.x - attack_point[0]
            dy = enemy.y - attack_point[1]
            dist = math.hypot(dx, dy)
            # Simple hit check using weapon range
            if dist < weapon.get('range', 50) * 0.5:
                dead = enemy.take_damage(damage)
                if dead:
                    self.enemies.remove(enemy)
                    # Reward player for kills
                    reward = getattr(enemy, 'money', 50)
                    self.money += reward
                    if self.hud:
                        self.hud.show_temporary_message('Enemy Down', f'+{self.hud.format_money(reward)}', (0, 255, 0), 3)
                else:
                    # Show hit feedback
                    if self.hud:
                        self.hud.show_temporary_message('Hit!', '', (255, 200, 0), 1)

    def spawn_enemies(self, count=8):
        """Spawn some enemies around the map."""
        self.enemies = []
        if not self.world:
            return
        for _ in range(count):
            x = random.randint(200, config.WORLD_SIZE - 200)
            y = random.randint(200, config.WORLD_SIZE - 200)
            self.enemies.append(Enemy(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == 'menu':
                action = self.main_menu.handle_event(event)
                if action == 'New Game':
                    self.start_new_game()
                elif action == 'Continue':
                    latest = self.save_system.get_latest_save()
                    if latest:
                        self.load_game(latest)
                elif action == 'Load Game':
                    self.state = 'load'
                    self.load_index = 0
                elif action == 'Settings':
                    self.state = 'settings'
                elif action == 'Exit Game':
                    self.running = False

            elif self.state == 'settings':
                res = self.settings_menu.handle_event(event, self)
                if res == 'back':
                    self.state = 'menu'

            elif self.state == 'load':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        if self.sound_manager:
                            self.sound_manager.play_sfx('opt_clicked')
                    elif event.key == pygame.K_UP:
                        self.load_index = max(0, getattr(self, 'load_index', 0) - 1)
                        if self.sound_manager:
                            self.sound_manager.play_sfx('button_scroll')
                    elif event.key == pygame.K_DOWN:
                        self.load_index = min(9, getattr(self, 'load_index', 0) + 1)
                        if self.sound_manager:
                            self.sound_manager.play_sfx('button_scroll')
                    elif event.key == pygame.K_RETURN:
                        # Load the selected slot (if it exists)
                        save = self.save_system.get_save_for_slot(self.load_index + 1)
                        if save:
                            if self.sound_manager:
                                self.sound_manager.play_sfx('opt_clicked')
                            self.load_game(save)

            elif self.state == 'playing':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                    elif event.key == pygame.K_TAB:
                        # Open radio wheel
                        self.radio_wheel_open = True
                        self.weapon_wheel_open = False
                        self.wheel_timer = 3.0
                    elif event.key == pygame.K_q:
                        # Open weapon wheel
                        self.weapon_wheel_open = True
                        self.radio_wheel_open = False
                        self.wheel_timer = 3.0
                    elif event.key == pygame.K_e:
                        # Interact with world (shops, safe houses, etc.)
                        if self.interact_text:
                            if 'Ammo' in self.interact_text:
                                self._buy_ammo()
                            elif 'Safe House' in self.interact_text:
                                self.save_at_safehouse()
                    elif event.key == pygame.K_SPACE:
                        if self.mission_manager and self.mission_manager.state in ('briefing', 'idle'):
                            self.mission_manager.advance_briefing(self)
                    elif self.weapon_wheel_open and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                        # Select weapon by number
                        if self.player:
                            idx = int(event.unicode) - 1
                            if 0 <= idx < len(self.player.weapons):
                                self.player.current_weapon = idx
                    elif self.radio_wheel_open and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                        # Only one station for now
                        pass

            elif self.state == 'paused':
                result = self.in_game_menu.handle_event(event, self)
                if result == 'close':
                    self.exit_confirm = False
                    self.state = 'playing'
                elif result == 'exit':
                    self.running = False

                # Save game when on Save Game tab and ENTER pressed
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.in_game_menu.tabs[self.in_game_menu.selected_tab] == 'Save Game':
                        success, save_data = self.save_system.save_game(self, slot=self.in_game_menu.save_slot)
                        if success and hasattr(self, 'hud'):
                            self.hud.show_temporary_message('Game Saved', f"Slot {self.in_game_menu.save_slot}", (0, 255, 0), 3)
                    elif self.in_game_menu.tabs[self.in_game_menu.selected_tab] == 'Exit':
                        self.exit_confirm = True

                # Confirm exit
                if self.exit_confirm and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.running = False
                    elif event.key == pygame.K_n:
                        self.exit_confirm = False

    def update(self, dt):
        # Ensure cursor visibility matches current state
        pygame.mouse.set_visible(self.state != 'playing')
        if self.state != 'playing':
            # Use a consistent menu cursor
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            # Stop ambient sound when not playing
            if self.sound_manager:
                self.sound_manager.stop_ambient()

        # Intro state: show splash and wait for intro duration
        if self.state == 'settings' and hasattr(self, 'settings_menu'):
            # allow settings menu to update timers (e.g. remap countdown)
            self.settings_menu.update(dt)
            # Apply any graphics changes immediately
            self.apply_graphics_settings()
        if self.state == 'intro':
            elapsed = pygame.time.get_ticks() - self.intro_start
            if elapsed >= self.intro_duration:
                self.state = 'menu'
                # Stop intro music after it finishes
                if self.sound_manager:
                    self.sound_manager.stop_music()
            return

        if self.state == 'playing':
            # hide cursor when playing
            pygame.mouse.set_visible(False)
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_buttons = pygame.mouse.get_pressed()

            # Handle enter/exit vehicle (toggle on F press)
            f_pressed = keys[pygame.K_f]
            if f_pressed and not self._f_pressed_last_frame:
                if self.player and self.car:
                    car_rect = self.car.get_rect().inflate(20, 20)
                    if self.player.is_on_foot and self.player.get_rect().colliderect(car_rect):
                        self.player.enter_vehicle(self.car)
                    elif not self.player.is_on_foot:
                        self.player.exit_vehicle()
                        self.car.driver = None

            self._f_pressed_last_frame = f_pressed

            # Update player and car
            if self.player:
                self.player.update(dt, keys, mouse_pos, mouse_buttons)
                if getattr(self.player, 'attack_hit', False):
                    self.handle_player_attack()
                    self.player.attack_hit = False

            if self.player and not self.player.is_on_foot:
                # Sync player to car
                self.player.x = self.car.x
                self.player.y = self.car.y
                self.car.driver = self.player

            if self.car:
                self.car.update(dt, keys if not self.player or not self.player.is_on_foot else keys)

            # Update world/time/mission
            if self.world:
                self.world.update(dt)
            if self.time_system:
                self.time_system.update(dt)
            if self.mission_manager:
                self.mission_manager.update(self.player if self.player else self.car, self, dt)

            # Update vehicles and enemies
            if self.vehicle_manager:
                self.vehicle_manager.update(dt, keys)
            if self.enemies:
                building_rects = [b['rect'] for b in self.world.buildings] if self.world else []
                for enemy in self.enemies:
                    enemy.update(dt, (self.player.x, self.player.y) if self.player else (0, 0), building_rects)

            # Update HUD messages
            if self.hud and hasattr(self.hud, 'update'):
                self.hud.update(dt)

            # Handle wheel overlays timeout
            if self.wheel_timer > 0:
                self.wheel_timer -= dt
                if self.wheel_timer <= 0:
                    self.wheel_timer = 0
                    self.radio_wheel_open = False
                    self.weapon_wheel_open = False

            # Update camera to follow player if on foot, otherwise car
            target = self.player if self.player and self.player.is_on_foot else self.car
            if target:
                self.camera.update(target.x, target.y)

            # Ambient audio (always on while playing)
            if self.world and self.sound_manager:
                # Always keep an ambient loop running for street ambiance
                self.sound_manager.play_ambient('street_ambiance', loops=-1, volume=0.4)

            # Collisions
            self.check_collisions()

            # Out of bounds / water = death and respawn
            if self.world and self.player:
                if self.world.is_in_water(self.player.x, self.player.y):
                    # Fail any active mission
                    if self.mission_manager:
                        self.mission_manager.fail_mission('You went out of bounds and died', self)
                    self.respawn_player(penalty=1500, reason='Out of bounds')

            # Auto respawn if health hits zero
            if self.player and self.player.health <= 0:
                self.respawn_player(penalty=1500, reason='You died')

            # Interact hint (ammo store, safehouse)
            self.interact_text = ''
            if self.world and self.player:
                player_pos = (self.player.x, self.player.y)

                # Safe house interaction (save/park)
                safe_loc = config.LOCATIONS.get('safe_house')
                if safe_loc:
                    dist_safe = math.hypot(player_pos[0] - safe_loc[0], player_pos[1] - safe_loc[1])
                    if dist_safe < 150:
                        self.interact_text = 'Press E to save/park at Safe House'

                # Ammo shop interaction (overrides safehouse if closer)
                shop_loc = config.LOCATIONS.get('ammo_store')
                if shop_loc:
                    dist_shop = math.hypot(player_pos[0] - shop_loc[0], player_pos[1] - shop_loc[1])
                    if dist_shop < 150:
                        self.interact_text = 'Press E to buy ammo at Neon Arms'

    def check_collisions(self):
        # Car collisions
        if self.car:
            car_rect = self.car.get_rect()
            hits = self.world.check_collisions(car_rect) if self.world else []
            if hits:
                self.car.speed *= -0.4
                for hit in hits:
                    dx = self.car.x - hit.centerx
                    dy = self.car.y - hit.centery
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist > 0:
                        push = 30 / dist
                        self.car.x += dx * push
                        self.car.y += dy * push

        # Player collisions
        if self.player and self.world:
            player_rect = self.player.get_rect()
            hits = self.world.check_collisions(player_rect)
            if hits:
                # Simple pushback to prevent getting stuck
                for hit in hits:
                    dx = self.player.x - hit.centerx
                    dy = self.player.y - hit.centery
                    dist = (dx**2 + dy**2) ** 0.5
                    if dist > 0:
                        push = 20 / dist
                        self.player.x += dx * push
                        self.player.y += dy * push

    def _buy_ammo(self):
        # Attempt to purchase ammo at the ammo shop
        if not self.player or not self.world:
            return
        shop_loc = config.LOCATIONS.get('ammo_store')
        if not shop_loc:
            return

        dist = math.hypot(self.player.x - shop_loc[0], self.player.y - shop_loc[1])
        if dist > 150:
            return

        # Determine current weapon
        weapon_key = self.player.weapons[self.player.current_weapon]
        price_info = config.AMMO_PRICES.get(weapon_key)
        if not price_info:
            self.hud.show_temporary_message('No ammo available for this weapon.', '', (255, 255, 0), 3)
            return

        price = price_info['price']
        amount = price_info['amount']
        if self.money < price:
            self.hud.show_temporary_message('Not enough cash.', '', (255, 0, 0), 3)
            return

        self.money -= price
        self.player.ammo[weapon_key] = self.player.ammo.get(weapon_key, 0) + amount
        self.hud.show_temporary_message(f'Bought {amount} {weapon_key} ammo', f'-{self.hud.format_money(price)}', (0, 255, 0), 4)

    def render(self):
        # Intro splash
        if self.state == 'intro':
            self.screen.fill((0, 0, 0))
            title = pygame.font.Font(None, 80).render('Griffin Presents:', True, (255, 255, 255))
            sub = pygame.font.Font(None, 64).render('NEON CITY', True, (255, 0, 128))
            bottom = pygame.font.Font(None, 24).render(
                'All content & material used is property of Kabelo Samkelo Kgosana & LTS. LTS est. 2024',
                True, (200, 200, 200)
            )
            self.screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, config.HEIGHT // 2 - 80))
            self.screen.blit(sub, (config.WIDTH // 2 - sub.get_width() // 2, config.HEIGHT // 2))
            self.screen.blit(bottom, (config.WIDTH // 2 - bottom.get_width() // 2, config.HEIGHT - 40))
            pygame.display.flip()
            return

        # Draw base
        self.screen.fill(config.COLORS['GRASS'])
        # ensure cursor visible in any non-playing state
        if self.state != 'playing':
            pygame.mouse.set_visible(True)
            pygame.mouse.set_cursor(*pygame.cursors.arrow)

        if self.state == 'menu':
            self.main_menu.draw(self.screen)
        elif self.state == 'settings':
            self.settings_menu.draw(self.screen)
        elif self.state == 'load':
            self.draw_load_screen()
        else:
            # Playing or paused
            if self.world:
                self.world.draw(self.screen, self.camera, self.time_system)

            # Draw other vehicles
            if self.vehicle_manager:
                self.vehicle_manager.draw(self.screen, self.camera, is_night=self.time_system.is_night() if self.time_system else False)

            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera)

            # Draw mission target
            if self.state in ['playing', 'paused'] and self.mission_manager and self.mission_manager.get_current_mission():
                self.mission_manager.draw_target(self.screen, self.camera)

            # Draw car and player
            if self.car:
                self.car.draw(self.screen, self.camera, is_night=self.time_system.is_night() if self.time_system else False)
            if self.player and self.player.is_on_foot:
                self.player.draw(self.screen, self.camera)

            # Night overlay (dimming)
            if self.time_system:
                overlay_color = self.time_system.get_overlay_color()
                if overlay_color:
                    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
                    overlay.fill(overlay_color)
                    self.screen.blit(overlay, (0, 0))

            # Brightness setting overlay from graphics menu
            if hasattr(self, 'settings_menu') and self.settings_menu.graphics_settings:
                bright = self.settings_menu.graphics_settings.get('brightness', 1.0)
                if bright < 1.0:
                    alpha = int((1.0 - bright) * 200)
                    dark = pygame.Surface((config.WIDTH, config.HEIGHT))
                    dark.fill((0, 0, 0))
                    dark.set_alpha(alpha)
                    self.screen.blit(dark, (0, 0))
                elif bright > 1.0:
                    alpha = int((bright - 1.0) * 200)
                    light = pygame.Surface((config.WIDTH, config.HEIGHT))
                    light.fill((255, 255, 255))
                    light.set_alpha(alpha)
                    self.screen.blit(light, (0, 0))

            # Draw HUD while playing or paused (shows waypoint/radar)
            if self.state in ('playing', 'paused') and self.hud:
                self.hud.draw(self.screen, self)

            # Radio / Weapon wheel overlays
            if self.radio_wheel_open or self.weapon_wheel_open:
                overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))

                font = pygame.font.Font(None, 48)
                small = pygame.font.Font(None, 28)

                if self.radio_wheel_open:
                    title = font.render('Radio Wheel', True, (255, 255, 255))
                    self.screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 150))
                    option = small.render('1) Neon Beats FM (Selected)', True, (200, 200, 255))
                    self.screen.blit(option, (config.WIDTH // 2 - option.get_width() // 2, 230))
                    hint = small.render('Press 1 to select. Press TAB to close.', True, (180, 180, 180))
                    self.screen.blit(hint, (config.WIDTH // 2 - hint.get_width() // 2, 280))

                if self.weapon_wheel_open and self.player:
                    title = font.render('Weapon Wheel', True, (255, 255, 255))
                    self.screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 150))
                    for idx, weapon_key in enumerate(self.player.weapons):
                        weapon = config.WEAPONS.get(weapon_key, {})
                        icon = weapon.get('icon', '?')
                        name = weapon.get('name', weapon_key)
                        selected = idx == self.player.current_weapon
                        color = (255, 255, 0) if selected else (200, 200, 200)
                        text = f"{idx+1}) {icon} {name}"
                        item_surf = small.render(text, True, color)
                        self.screen.blit(item_surf, (config.WIDTH // 2 - item_surf.get_width() // 2, 220 + idx * 30))
                    hint = small.render('Press 1-5 to select. Press Q to close.', True, (180, 180, 180))
                    self.screen.blit(hint, (config.WIDTH // 2 - hint.get_width() // 2, 400))

            if self.state == 'paused':
                self.in_game_menu.draw(self.screen, self)

        pygame.display.flip()

    def draw_load_screen(self):
        # Simple load game screen
        self.screen.fill((10, 10, 25))
        font = pygame.font.Font(None, 48)
        title = font.render('Load Game', True, (255, 255, 255))
        self.screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 50))

        saves = self.save_system.get_save_files()

        start_y = 140
        slot_height = 40
        for slot in range(1, 11):
            save = self.save_system.get_save_for_slot(slot)
            selected = slot - 1 == getattr(self, 'load_index', 0)
            color = (255, 255, 255) if selected else (150, 150, 150)

            if save:
                timestamp = save.get('timestamp', 0)
                import time
                time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(timestamp)) if timestamp else 'Unknown'
                mission = save.get('game_state', {}).get('mission', {})
                mission_index = mission.get('current_index', 0)
                mission_title = ''
                # Mission title may not be stored; show index
                mission_title = f"Mission {mission_index + 1}"
                label = f"{slot}. {save.get('name', 'Save')} ({mission_title}) - {time_str}"
            else:
                label = f"{slot}. EMPTY"

            text = pygame.font.Font(None, 28).render(label, True, color)
            self.screen.blit(text, (config.WIDTH // 2 - text.get_width() // 2, start_y + (slot - 1) * slot_height))

        hint = pygame.font.Font(None, 24).render('Use Up/Down to select, Enter to load, ESC to return', True, (150, 150, 150))
        self.screen.blit(hint, (config.WIDTH // 2 - hint.get_width() // 2, config.HEIGHT - 60))

    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()
