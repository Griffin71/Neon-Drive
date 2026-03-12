import pygame
import config

class MainMenu:
    def __init__(self, save_system, sound_manager=None):
        self.save_system = save_system
        self.sound_manager = sound_manager
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Menu options
        self.options = ['New Game', 'Continue', 'Load Game', 'Settings', 'Exit Game']
        self.selected = 0
        
        # Animation
        self.title_offset = 0
        self.anim_timer = 0
        
    def get_visible_options(self):
        has_saves = self.save_system.has_saves()
        options = []
        for option in self.options:
            if option == 'Continue' and not has_saves:
                continue
            options.append(option)
        return options

    def handle_event(self, event):
        options = self.get_visible_options()
        if not options:
            return None

        # Keep selection within current visible options
        self.selected = min(self.selected, len(options) - 1)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                if self.sound_manager:
                    self.sound_manager.play_sfx('button_scroll')

            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(options)
            elif event.key == pygame.K_RETURN:
                if self.sound_manager:
                    self.sound_manager.play_sfx('opt_clicked')
                return options[self.selected]
            elif event.key == pygame.K_1:
                self.selected = 0
            elif event.key == pygame.K_2 and len(options) > 1:
                self.selected = 1
            elif event.key == pygame.K_3 and len(options) > 2:
                self.selected = 2
            elif event.key == pygame.K_4 and len(options) > 3:
                self.selected = 3
            elif event.key == pygame.K_5 and len(options) > 4:
                self.selected = 4
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # check if a menu option was clicked
            mx, my = event.pos
            y_start = 300
            spacing = 60
            for i, option in enumerate(options):
                text_surf = self.font_menu.render(option, True, (255,255,255))
                x = config.WIDTH // 2 - text_surf.get_width() // 2
                y = y_start + i * spacing
                rect = pygame.Rect(x - 20, y - 10, text_surf.get_width() + 40, text_surf.get_height() + 20)
                if rect.collidepoint(mx, my):
                    self.selected = i
                    if self.sound_manager:
                        self.sound_manager.play_sfx('opt_clicked')
                    return options[self.selected]
        return None
                
        return None
        
    def update(self, dt):
        self.anim_timer += dt
        self.title_offset = 5 * pygame.math.Vector2(1, 0).rotate(self.anim_timer * 30).x
        
    def draw(self, screen):
        screen.fill((10, 10, 25))
        
        # Animated background gradient
        for i in range(0, config.HEIGHT, 20):
            color_val = int(10 + (i / config.HEIGHT) * 20)
            pygame.draw.rect(screen, (color_val, color_val, color_val + 15), 
                           (0, i, config.WIDTH, 20))
        
        # Title with glow effect
        title_text = "NEON CITY DRIVE"
        
        # Glow
        glow_surf = self.font_title.render(title_text, True, (255, 0, 128))
        for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
            screen.blit(glow_surf, 
                       (config.WIDTH // 2 - glow_surf.get_width() // 2 + offset[0] + int(self.title_offset),
                        100 + offset[1]))
            
        # Main title
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        screen.blit(title_surf, 
                   (config.WIDTH // 2 - title_surf.get_width() // 2 + int(self.title_offset), 100))
        
        # Subtitle
        subtitle = self.font_small.render("An Open World Crime Adventure", True, (200, 100, 150))
        screen.blit(subtitle, (config.WIDTH // 2 - subtitle.get_width() // 2, 170))
        
        # Draw menu options
        options = self.get_visible_options()
        y_start = 300
        spacing = 60
        
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == self.selected else (150, 150, 150)
            
            # Highlight selected
            if i == self.selected:
                # Selection indicator
                pygame.draw.polygon(screen, (255, 0, 128), 
                                  [(config.WIDTH // 2 - 200, y_start + i * spacing - 10),
                                   (config.WIDTH // 2 - 220, y_start + i * spacing + 5),
                                   (config.WIDTH // 2 - 200, y_start + i * spacing + 20)])
                
                # Highlight background
                s = self.font_menu.render(option, True, color)
                screen.blit(s, (config.WIDTH // 2 - s.get_width() // 2, y_start + i * spacing))
                
                # Arrow
                arrow = self.font_menu.render("►", True, (255, 0, 128))
                screen.blit(arrow, (config.WIDTH // 2 - 220, y_start + i * spacing))
                screen.blit(arrow, (config.WIDTH // 2 + 180, y_start + i * spacing))
            else:
                s = self.font_menu.render(option, True, color)
                screen.blit(s, (config.WIDTH // 2 - s.get_width() // 2, y_start + i * spacing))
                
        # Version
        version = self.font_small.render("v1.0.0", True, (100, 100, 100))
        screen.blit(version, (10, config.HEIGHT - 30))
        
        # Controls hint (center)
        controls = self.font_small.render("Arrow Keys + Mouse to navigate  |  ENTER to select", True, (100, 100, 100))
        screen.blit(controls, (config.WIDTH // 2 - controls.get_width() // 2, config.HEIGHT - 40))

        # remove duplicate bottom-right hint to reduce clutter

