import pygame
import config

class TimeSystem:
    def __init__(self):
        self.game_hour = 12  # Start at noon
        self.game_minute = 0
        self.real_time_accum = 0
        
        # Seconds per in-game minute (config.TIME_SCALE)
        self.seconds_per_minute = config.TIME_SCALE
        
    def update(self, dt):
        self.real_time_accum += dt
        
        # Advance time by minutes
        while self.real_time_accum >= self.seconds_per_minute:
            self.real_time_accum -= self.seconds_per_minute
            self.game_minute += 1
            
            if self.game_minute >= 60:
                self.game_minute = 0
                self.game_hour += 1
                if self.game_hour >= 24:
                    self.game_hour = 0
            
    def get_time_string(self):
        hour = self.game_hour
        minute = self.game_minute
        am_pm = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
            
        return f"{display_hour}:{minute:02d} {am_pm}"
        
    def get_phase(self):
        hour = self.game_hour
        
        for phase_name, phase_data in config.TIME_PHASES.items():
            if phase_data['start'] <= hour < phase_data['end']:
                return phase_name, phase_data
                
        # Default to night
        return 'night', config.TIME_PHASES['night']
        
    def get_brightness(self):
        _, phase_data = self.get_phase()
        return phase_data['brightness']
        
    def is_night(self):
        phase, _ = self.get_phase()
        return phase in ['night', 'midnight']
        
    def is_day(self):
        phase, _ = self.get_phase()
        return phase in ['morning', 'midday', 'afternoon']
        
    def get_overlay_color(self):
        # Night dimming overlay from 20:00 to 06:00 (30% darker).
        hour = self.game_hour
        if hour >= 20 or hour < 6:
            return (0, 0, 0, 80)
        return None
            
    def draw_time(self, screen, font):
        time_str = self.get_time_string()
        phase_name, _ = self.get_phase()
        
        # Background for time
        time_text = font.render(time_str, True, (255, 255, 255))
        phase_text = font.render(phase_name.title(), True, (200, 200, 200))
        
        # Draw at top center
        screen.blit(time_text, (config.WIDTH // 2 - time_text.get_width() // 2, 10))
        screen.blit(phase_text, (config.WIDTH // 2 - phase_text.get_width() // 2, 35))
        
    def advance_to_next_day(self):
        """Advance to next day - for mission timing"""
        self.game_hour = 8  # 8 AM
        self.game_minute = 0
        self.real_time_accum = 0

