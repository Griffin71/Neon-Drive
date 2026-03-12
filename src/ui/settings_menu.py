import pygame
import config

class SettingsMenu:
    def __init__(self, sound_manager=None):
        self.sound_manager = sound_manager
        self.font_title = pygame.font.Font(None, 56)
        self.font_menu = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)
        
        # Main categories
        self.categories = ['Controls', 'Graphics', 'Sound']
        self.selected_category = 0
        
        # Sub-sections and selection indices
        self.control_sections = ['On Foot', 'In Vehicle']
        self.selected_control_section = 0
        self.selected_control_index_per_section = [0, 0]  # index of action in each section

        # Graphics settings (expanded)
        self.graphics_settings = {
            'resolution': 1,
            'screen_type': 0,
            'show_overlay': False,
            'overlay_position': 0,
            'brightness': 1.0,
            'saturation': 1.0,
        }
        # positions for debug overlay
        self.debug_positions = ['top-left','top-center','top-right','side-center','bottom-left','bottom-center','bottom-right']
        self.selected_graphics_index = 0  # which row is selected for navigation

        # Sound settings
        self.sound_settings = {
            'world_volume': 0.5,
            'sfx_volume': 0.7,
            'radio_volume': 0.6,
        }
        self.selected_sound_index = 0
        
        # remapping state
        self.remapping = False            # entering confirmation or active remap
        self.waiting_for_key = False      # waiting for user to press new key
        self.remap_section = None
        self.remap_action = None
        self.remap_original = None
        self.remap_timer = 0.0
        self.remap_confirm = False
        
        self.active = True
        self.scrolling = {'controls': 0}
        
    def handle_event(self, event, game=None):
        # universal cancel
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.sound_manager:
                self.sound_manager.play_sfx('opt_clicked')
            return 'back'

        # if waiting for the player to press a new key for remapping
        if self.waiting_for_key:
            if event.type == pygame.KEYDOWN:
                new_key = pygame.key.name(event.key)
                controls = config.CONTROLS.get(self.remap_section, {})
                # swap if already used by another action
                conflict = None
                for act, val in controls.items():
                    if val == new_key and act != self.remap_action:
                        conflict = act
                        break
                if conflict:
                    # swap values
                    controls[conflict] = controls.get(self.remap_action, '')
                # assign new key
                controls[self.remap_action] = new_key
                # begin confirmation phase
                self.waiting_for_key = False
                self.remapping = True
                self.remap_confirm = True
                self.remap_timer = 15.0
            return None

        # remapping confirmation
        if self.remapping:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # accept change
                    self.remapping = False
                    self.remap_confirm = False
                    self.remap_timer = 0
                elif event.key == pygame.K_n:
                    # revert
                    if self.remap_original and self.remap_section:
                        config.CONTROLS[self.remap_section] = self.remap_original
                    self.remapping = False
                    self.remap_confirm = False
                    self.remap_timer = 0
            return None

        # keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                if self.sound_manager:
                    self.sound_manager.play_sfx('button_scroll')
            if event.key == pygame.K_TAB:
                # Switch category
                self.selected_category = (self.selected_category + 1) % len(self.categories)
                if self.sound_manager:
                    self.sound_manager.play_sfx('button_scroll')
            elif event.key == pygame.K_1:
                self.selected_category = 0
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_2:
                self.selected_category = 1
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
            elif event.key == pygame.K_3:
                self.selected_category = 2
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')

            # category-specific navigation
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                if self.selected_category == 0:  # controls
                    section = self.selected_control_section
                    items = list(config.CONTROLS['on_foot' if section == 0 else 'vehicle'].items())
                    idx = self.selected_control_index_per_section[section]
                    if event.key == pygame.K_UP:
                        idx = (idx - 1) % len(items)
                    else:
                        idx = (idx + 1) % len(items)
                    self.selected_control_index_per_section[section] = idx
                elif self.selected_category == 1:  # graphics
                    max_idx = 5
                    if event.key == pygame.K_UP:
                        self.selected_graphics_index = max(0, self.selected_graphics_index - 1)
                    else:
                        self.selected_graphics_index = min(max_idx, self.selected_graphics_index + 1)
                elif self.selected_category == 2:  # sound
                    max_idx = 2
                    if event.key == pygame.K_UP:
                        self.selected_sound_index = max(0, self.selected_sound_index - 1)
                    else:
                        self.selected_sound_index = min(max_idx, self.selected_sound_index + 1)

            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.navigate_horizontal(-1 if event.key == pygame.K_LEFT else 1)

            if event.key == pygame.K_RETURN:
                if self.selected_category == 0:  # start remap for selected control
                    section = 'on_foot' if self.selected_control_section == 0 else 'vehicle'
                    idx = self.selected_control_index_per_section[self.selected_control_section]
                    action = list(config.CONTROLS[section].keys())[idx]
                    self.start_remap(section, action)
        # mouse navigation
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # check category tabs
            tab_width = 200
            tab_start = (config.WIDTH - len(self.categories) * tab_width) // 2
            for i in range(len(self.categories)):
                rect = pygame.Rect(tab_start + i*tab_width, 90, tab_width, 40)
                if rect.collidepoint(mx, my):
                    self.selected_category = i
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                    return None
            # category-specific clicks
            if self.selected_category == 0:
                # controls list click detection
                section_y = 160 + 60
                items = config.CONTROLS['on_foot' if self.selected_control_section == 0 else 'vehicle']
                for idx, key in enumerate(items.keys()):
                    y_pos = section_y + idx * 45
                    area = pygame.Rect(200, y_pos, 300, 30)
                    if area.collidepoint(mx, my):
                        self.selected_control_index_per_section[self.selected_control_section] = idx
                        self.start_remap('on_foot' if self.selected_control_section==0 else 'vehicle', key)
                        return None
            elif self.selected_category == 1:
                # graphics click: adjust that row
                row = (my - 160) // 60
                if 0 <= row <= 5:
                    self.selected_graphics_index = row
                    self.navigate_horizontal(1)
                    return None
            elif self.selected_category == 2:
                row = (my - 160) // 100
                if 0 <= row <= 2:
                    self.selected_sound_index = row
                    self.navigate_horizontal(1)
                    return None
        return None
        
    def navigate_vertical(self, direction):
        if self.selected_category == 0:  # Controls
            if direction < 0:
                self.selected_control_section = (self.selected_control_section - 1) % len(self.control_sections)
            else:
                self.selected_control_section = (self.selected_control_section + 1) % len(self.control_sections)
                
    def navigate_horizontal(self, direction):
        if self.selected_category == 1:  # Graphics
            idx = self.selected_graphics_index
            if idx == 0:  # Resolution
                new_res = self.graphics_settings['resolution'] + direction
                if 0 <= new_res < len(config.GRAPHICS_SETTINGS['resolutions']):
                    self.graphics_settings['resolution'] = new_res
            elif idx == 1:  # Screen type
                new_type = self.graphics_settings['screen_type'] + direction
                if 0 <= new_type < len(config.GRAPHICS_SETTINGS['screen_types']):
                    self.graphics_settings['screen_type'] = new_type
            elif idx == 2:  # toggle overlay
                if direction != 0:
                    self.graphics_settings['show_overlay'] = not self.graphics_settings['show_overlay']
            elif idx == 3:  # position
                pos = self.graphics_settings['overlay_position'] + direction
                if pos < 0:
                    pos = len(self.debug_positions) - 1
                elif pos >= len(self.debug_positions):
                    pos = 0
                self.graphics_settings['overlay_position'] = pos
            elif idx == 4:  # brightness
                self.graphics_settings['brightness'] = max(0.0, min(2.0, self.graphics_settings['brightness'] + direction * 0.1))
            elif idx == 5:  # saturation
                self.graphics_settings['saturation'] = max(0.0, min(2.0, self.graphics_settings['saturation'] + direction * 0.1))
        elif self.selected_category == 2:  # Sound
            # adjust selected sound index
            if self.selected_sound_index == 0:
                self.sound_settings['world_volume'] = max(0, min(1, self.sound_settings['world_volume'] + direction * 0.1))
            elif self.selected_sound_index == 1:
                self.sound_settings['sfx_volume'] = max(0, min(1, self.sound_settings['sfx_volume'] + direction * 0.1))
            elif self.selected_sound_index == 2:
                self.sound_settings['radio_volume'] = max(0, min(1, self.sound_settings['radio_volume'] + direction * 0.1))

    def start_remap(self, section, action_key):
        # begin remapping a control; save original state for rollback
        self.remapping = True
        self.remap_section = section
        self.remap_action = action_key
        self.remap_original = config.CONTROLS[section].copy()
        self.remap_timer = 15.0
        self.remap_confirm = True

    def update(self, dt):
        # handle remap timer and automatic rollback
        if self.remapping and self.remap_confirm:
            self.remap_timer -= dt
            if self.remap_timer <= 0:
                # time expired, revert
                if self.remap_original and self.remap_section:
                    config.CONTROLS[self.remap_section] = self.remap_original
                self.remapping = False
                self.remap_confirm = False
                self.remap_timer = 0
                    
    def draw(self, screen):
        screen.fill((15, 15, 30))
        
        # Header
        title = self.font_title.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 30))
        
        # Category tabs
        tab_width = 200
        tab_start = (config.WIDTH - len(self.categories) * tab_width) // 2
        
        for i, cat in enumerate(self.categories):
            color = (255, 0, 128) if i == self.selected_category else (100, 100, 100)
            s = self.font_menu.render(cat, True, color)
            pygame.draw.rect(screen, color if i == self.selected_category else (50, 50, 50),
                           (tab_start + i * tab_width, 90, tab_width, 40),
                           1 if i != self.selected_category else 0)
            screen.blit(s, (tab_start + i * tab_width + tab_width // 2 - s.get_width() // 2, 95))
            
        # Draw content based on category
        if self.selected_category == 0:
            self.draw_controls(screen)
        elif self.selected_category == 1:
            self.draw_graphics(screen)
        elif self.selected_category == 2:
            self.draw_sound(screen)
            
        # Controls hint
        hint = self.font_small.render("TAB: Switch Category  |  ←→: Adjust  |  ESC: Back", True, (100, 100, 100))
        screen.blit(hint, (config.WIDTH // 2 - hint.get_width() // 2, config.HEIGHT - 40))

        # Navigation help (arrow keys or mouse)
        help_text = self.font_small.render("Arrow Keys + Mouse: Navigate  |  ENTER: Select", True, (150, 150, 150))
        screen.blit(help_text, (config.WIDTH - help_text.get_width() - 20, config.HEIGHT - 40))
        
    def draw_controls(self, screen):
        # Section selector
        section_width = 300
        section_start = (config.WIDTH - len(self.control_sections) * section_width) // 2
        
        y = 160
        
        # Section tabs
        for i, section in enumerate(self.control_sections):
            color = (255, 255, 255) if i == self.selected_control_section else (150, 150, 150)
            s = self.font_menu.render(section, True, color)
            pygame.draw.rect(screen, (60, 60, 80) if i == self.selected_control_section else (40, 40, 50),
                           (section_start + i * section_width, y, section_width, 35),
                           1 if i != self.selected_control_section else 0)
            if i == self.selected_control_section:
                pygame.draw.rect(screen, (255, 0, 128),
                               (section_start + i * section_width, y, section_width, 35), 2)
            screen.blit(s, (section_start + i * section_width + section_width // 2 - s.get_width() // 2, y + 5))
            
        # Draw controls list
        y += 60
        controls = config.CONTROLS['on_foot' if self.selected_control_section == 0 else 'vehicle']
        section = 0 if self.selected_control_section == 0 else 1

        # Title
        title = self.font_title.render(f"{self.control_sections[self.selected_control_section]} Controls", True, (200, 200, 200))
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, y))
        
        y += 50
        
        # Control bindings
        control_items = list(controls.items())
        
        for idx, (key, value) in enumerate(control_items):
            # highlight selected row
            is_selected = (idx == self.selected_control_index_per_section[section])
            row_y = y + idx * 45
            if is_selected:
                pygame.draw.rect(screen, (50, 50, 80), (190, row_y - 2, 300, 30))

            # Key name
            key_name = key.replace('_', ' ').title()
            key_surf = self.font_small.render(key_name, True, (255, 255, 255))
            screen.blit(key_surf, (200, row_y))
            
            # Key binding
            value_surf = self.font_small.render(value, True, (255, 0, 128))
            screen.blit(value_surf, (200 + 180, row_y))
            
            # Underline
            pygame.draw.line(screen, (60, 60, 80), (200, row_y + 25), (200 + 280, row_y + 25), 1)

        # if currently remapping, overlay message
        if self.remapping and self.remap_confirm:
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(220)
            screen.blit(overlay, (0, 0))
            msg = self.font_title.render('Confirm key change? (Y/N)', True, (255, 255, 255))
            screen.blit(msg, (config.WIDTH//2 - msg.get_width()//2, config.HEIGHT//2 - 40))
            timer_text = self.font_menu.render(f'Reverting in {int(self.remap_timer)}s', True, (200, 200, 200))
            screen.blit(timer_text, (config.WIDTH//2 - timer_text.get_width()//2, config.HEIGHT//2 + 20))
        
            
    def draw_graphics(self, screen):
        y = 160
        rows = [
            ('Resolution', lambda: str(config.GRAPHICS_SETTINGS['resolutions'][self.graphics_settings['resolution']])),
            ('Screen Type', lambda: config.GRAPHICS_SETTINGS['screen_types'][self.graphics_settings['screen_type']]),
            ('Debug Overlay', lambda: 'On' if self.graphics_settings['show_overlay'] else 'Off'),
            ('Overlay Pos', lambda: self.debug_positions[self.graphics_settings['overlay_position']]),
            ('Brightness', lambda: f"{int(self.graphics_settings['brightness']*100)}%"),
            ('Saturation', lambda: f"{int(self.graphics_settings['saturation']*100)}%"),
        ]
        for idx, (title, valfunc) in enumerate(rows):
            selected = (idx == self.selected_graphics_index)
            color = (255, 255, 0) if selected else (255, 255, 255)
            title_surf = self.font_menu.render(title + ':', True, color)
            screen.blit(title_surf, (config.WIDTH//2 - 200, y))
            value_surf = self.font_menu.render(valfunc(), True, color)
            screen.blit(value_surf, (config.WIDTH//2 + 50, y))
            y += 60

    def draw_setting_section(self, screen, title, y, selected_index, options):
        # Title
        title_surf = self.font_title.render(title, True, (200, 200, 200))
        screen.blit(title_surf, (config.WIDTH // 2 - title_surf.get_width() // 2, y))
        
        y += 50
        
        # Options
        option_width = 180
        total_width = len(options) * option_width
        start_x = (config.WIDTH - total_width) // 2
        
        for i, option in enumerate(options):
            x = start_x + i * option_width
            
            color = (255, 255, 255) if i == selected_index else (120, 120, 120)
            bg_color = (60, 60, 80) if i == selected_index else (40, 40, 50)
            
            # Box
            pygame.draw.rect(screen, bg_color, (x, y, option_width - 10, 40))
            if i == selected_index:
                pygame.draw.rect(screen, (255, 0, 128), (x, y, option_width - 10, 40), 2)
            else:
                pygame.draw.rect(screen, (80, 80, 100), (x, y, option_width - 10, 40), 1)
                
            # Text
            text_surf = self.font_small.render(option.title(), True, color)
            screen.blit(text_surf, (x + option_width // 2 - text_surf.get_width() // 2, y + 8))
            
    def draw_sound(self, screen):
        y = 160
        # Sound sections
        sections = ['World Volume', 'SFX Volume', 'Radio Volume']
        values = [
            self.sound_settings['world_volume'],
            self.sound_settings['sfx_volume'],
            self.sound_settings['radio_volume'],
        ]
        for i, (section, value) in enumerate(zip(sections, values)):
            self.draw_volume_slider(screen, section, y, value, i == self.selected_sound_index)
            y += 100
            
    def draw_volume_slider(self, screen, title, y, value, selected):
        # Title
        title_surf = self.font_title.render(title, True, (200, 200, 200) if not selected else (255, 255, 0))
        screen.blit(title_surf, (config.WIDTH // 2 - title_surf.get_width() // 2, y))
        
        y += 50
        
        # Slider
        slider_width = 400
        slider_x = (config.WIDTH - slider_width) // 2
        
        # Track
        track_color = (40, 40, 50)
        border_color = (80, 80, 100)
        if selected:
            border_color = (255, 255, 0)
        pygame.draw.rect(screen, track_color, (slider_x, y, slider_width, 20))
        pygame.draw.rect(screen, border_color, (slider_x, y, slider_width, 20), 1)
        
        # Fill
        fill_width = int(slider_width * value)
        pygame.draw.rect(screen, (255, 0, 128), (slider_x, y, fill_width, 20))
        
        # Handle
        handle_x = slider_x + fill_width
        pygame.draw.circle(screen, (255, 255, 255), (handle_x, y + 10), 8)
        
        # Value text
        value_text = f"{int(value * 100)}%"
        value_surf = self.font_small.render(value_text, True, (255, 255, 255))
        screen.blit(value_surf, (slider_x + slider_width + 20, y))

