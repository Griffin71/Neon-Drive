import pygame
import random
import config

class World:
    def __init__(self):
        self.buildings = []
        self.roads = []
        self.lakes = []
        self.street_lights = []
        self.pois = {}  # Points of interest (police station, etc)
        self.water_boundary = None
        self.land_area = None
        
        # Generate world elements
        self.generate_water_boundary()
        self.generate_lakes()
        self.generate_roads()
        self.generate_buildings()
        self.generate_street_lights()
        self.generate_pois()
        
    def generate_water_boundary(self):
        """Create water surrounding the map like GTA"""
        water_width = config.MAP_BOUNDARY['water_width']
        world_size = config.WORLD_SIZE
        
        # Water is everywhere outside the playable area
        self.land_area = pygame.Rect(
            water_width, 
            water_width, 
            world_size - water_width * 2, 
            world_size - water_width * 2
        )
        
    def generate_lakes(self):
        """Generate lakes and dams in the world"""
        # Main lake (central area)
        self.lakes.append({
            'rect': pygame.Rect(2500, 1500, 600, 400),
            'type': 'lake'
        })
        
        # Small pond
        self.lakes.append({
            'rect': pygame.Rect(800, 2800, 300, 250),
            'type': 'pond'
        })
        
    def generate_roads(self):
        """Generate road network"""
        world_size = config.WORLD_SIZE
        water_width = config.MAP_BOUNDARY['water_width']
        
        # Main horizontal roads
        for y in range(water_width + 300, world_size - water_width - 200, 600):
            self.roads.append({
                'rect': pygame.Rect(water_width, y, world_size - water_width * 2, 40),
                'type': 'highway'
            })
            
        # Main vertical roads
        for x in range(water_width + 300, world_size - water_width - 200, 600):
            self.roads.append({
                'rect': pygame.Rect(x, water_width, 40, world_size - water_width * 2),
                'type': 'highway'
            })
            
        # Side streets (smaller roads)
        for y in range(water_width + 500, world_size - water_width - 400, 300):
            if random.random() < 0.6:
                self.roads.append({
                    'rect': pygame.Rect(water_width, y, world_size - water_width * 2, 25),
                    'type': 'street'
                })
                
        for x in range(water_width + 500, world_size - water_width - 400, 300):
            if random.random() < 0.6:
                self.roads.append({
                    'rect': pygame.Rect(x, water_width, 25, world_size - water_width * 2),
                    'type': 'street'
                })
                
    def generate_buildings(self):
        """Generate buildings avoiding roads and lakes"""
        random.seed(42)
        water_width = config.MAP_BOUNDARY['water_width']
        
        # Building colors by district
        district_colors = [
            (80, 80, 100),   # Downtown - dark blue
            (100, 80, 60),   # Midtown - brown
            (60, 100, 60),   # Suburbs - green tint
            (120, 100, 80),  # Industrial - tan
            (90, 90, 90),    # Residential - gray
        ]
        
        for _ in range(150):
            # Try to find valid position
            valid = False
            attempts = 0
            
            while not valid and attempts < 50:
                x = random.randint(water_width + 50, config.WORLD_SIZE - water_width - 250)
                y = random.randint(water_width + 50, config.WORLD_SIZE - water_width - 250)
                w = random.randint(80, 250)
                h = random.randint(80, 250)
                
                test_rect = pygame.Rect(x, y, w, h)
                
                # Check collision with roads
                road_collision = False
                for road in self.roads:
                    if test_rect.colliderect(road['rect']):
                        road_collision = True
                        break
                        
                # Check collision with lakes
                lake_collision = False
                for lake in self.lakes:
                    if test_rect.colliderect(lake['rect']):
                        lake_collision = True
                        break
                        
                # Check collision with existing buildings
                building_collision = False
                for b in self.buildings:
                    if test_rect.colliderect(b['rect'].inflate(30, 30)):
                        building_collision = True
                        break
                        
                if not road_collision and not lake_collision and not building_collision:
                    # Determine district based on position
                    if x < 1500 and y < 1500:
                        color = district_colors[0]  # Downtown
                    elif x > 2500 and y > 2500:
                        color = district_colors[2]  # Suburbs
                    elif x > 2000:
                        color = district_colors[3]  # Industrial
                    else:
                        color = random.choice(district_colors)
                        
                    self.buildings.append({
                        'rect': test_rect,
                        'color': color,
                        'height': random.randint(3, 12),
                        'windows': random.randint(2, 8)
                    })
                    valid = True
                    
                attempts += 1
                
    def generate_street_lights(self):
        """Generate street lights along roads"""
        # Place lights along major roads
        for road in self.roads:
            if road['type'] == 'highway':
                # Horizontal road
                if road['rect'].width > road['rect'].height:
                    x = road['rect'].x
                    y_center = road['rect'].centery
                    while x < road['rect'].right:
                        self.street_lights.append({
                            'x': x,
                            'y': y_center - 30,
                            'type': 'highway'
                        })
                        self.street_lights.append({
                            'x': x,
                            'y': y_center + 30,
                            'type': 'highway'
                        })
                        x += 150
                # Vertical road
                else:
                    y = road['rect'].y
                    x_center = road['rect'].centerx
                    while y < road['rect'].bottom:
                        self.street_lights.append({
                            'x': x_center - 30,
                            'y': y,
                            'type': 'highway'
                        })
                        self.street_lights.append({
                            'x': x_center + 30,
                            'y': y,
                            'type': 'highway'
                        })
                        y += 150
            else:
                # Street lights
                if road['rect'].width > road['rect'].height:
                    x = road['rect'].x
                    y_center = road['rect'].centery
                    while x < road['rect'].right:
                        self.street_lights.append({
                            'x': x,
                            'y': y_center - 20,
                            'type': 'street'
                        })
                        self.street_lights.append({
                            'x': x,
                            'y': y_center + 20,
                            'type': 'street'
                        })
                        x += 120
                else:
                    y = road['rect'].y
                    x_center = road['rect'].centerx
                    while y < road['rect'].bottom:
                        self.street_lights.append({
                            'x': x_center - 20,
                            'y': y,
                            'type': 'street'
                        })
                        self.street_lights.append({
                            'x': x_center + 20,
                            'y': y,
                            'type': 'street'
                        })
                        y += 120
                        
    def generate_pois(self):
        """Generate police station and other points of interest"""
        police_loc = config.LOCATIONS.get('police_station', (3500, 3500))
        
        # Police station (large building)
        self.pois['police_station'] = {
            'x': police_loc[0],
            'y': police_loc[1],
            'type': 'police_station',
            'width': 300,
            'height': 250,
            'color': (30, 50, 120),  # Dark blue
        }
                
    def is_in_water(self, x, y):
        """Check if position is in water (outside playable area)"""
        return not self.land_area.collidepoint(x, y)
        
    def is_on_road(self, x, y):
        """Check if position is on a road"""
        for road in self.roads:
            if road['rect'].collidepoint(x, y):
                return True, road['type']
        return False, None
        
    def update(self, dt):
        pass
        
    def check_collisions(self, rect):
        return [b['rect'] for b in self.buildings if rect.colliderect(b['rect'])]
        
    def draw(self, screen, camera, time_system=None):
        water_width = config.MAP_BOUNDARY['water_width']
        
        # Draw water (background)
        screen.fill(config.COLORS['WATER'])
        
        # Draw land area (grass)
        land_rect = pygame.Rect(
            water_width - camera.x,
            water_width - camera.y,
            config.WORLD_SIZE - water_width * 2,
            config.WORLD_SIZE - water_width * 2
        )
        pygame.draw.rect(screen, config.COLORS['GRASS'], land_rect)
        
        # Draw darker grass pattern
        for i in range(0, config.WORLD_SIZE, 100):
            for j in range(0, config.WORLD_SIZE, 100):
                if (i + j) % 200 == 0:
                    rect = pygame.Rect(i - camera.x, j - camera.y, 50, 50)
                    if self.land_area.colliderect(pygame.Rect(i, j, 50, 50)):
                        pygame.draw.rect(screen, config.COLORS['DARK_GRASS'], rect)
                        
        # Draw lakes
        for lake in self.lakes:
            lake_rect = pygame.Rect(
                lake['rect'].x - camera.x,
                lake['rect'].y - camera.y,
                lake['rect'].width,
                lake['rect'].height
            )
            
            if lake['type'] == 'lake':
                pygame.draw.rect(screen, config.COLORS['LAKE'], lake_rect)
                # Lake border/shore
                pygame.draw.rect(screen, (100, 150, 100), lake_rect, 15)
            else:
                pygame.draw.rect(screen, (40, 120, 180), lake_rect)
                
        # Draw roads
        for road in self.roads:
            road_rect = pygame.Rect(
                road['rect'].x - camera.x,
                road['rect'].y - camera.y,
                road['rect'].width,
                road['rect'].height
            )
            
            # Check if visible
            if (-200 < road_rect.right and road_rect.left < config.WIDTH + 200 and
                -200 < road_rect.bottom and road_rect.top < config.HEIGHT + 200):
                
                # Road surface
                if road['type'] == 'highway':
                    pygame.draw.rect(screen, config.COLORS['ROAD'], road_rect)
                    # Road lines (center)
                    if road['rect'].width > road['rect'].height:
                        # Horizontal highway
                        line_y = road_rect.centery
                        pygame.draw.line(screen, config.COLORS['ROAD_LINE'],
                                       (road_rect.left, line_y),
                                       (road_rect.right, line_y), 2)
                    else:
                        # Vertical highway
                        line_x = road_rect.centerx
                        pygame.draw.line(screen, config.COLORS['ROAD_LINE'],
                                       (line_x, road_rect.top),
                                       (line_x, road_rect.bottom), 2)
                else:
                    # Street
                    pygame.draw.rect(screen, (70, 70, 70), road_rect)
                    
        # Draw buildings
        for b in self.buildings:
            b_rect = pygame.Rect(
                b['rect'].x - camera.x,
                b['rect'].y - camera.y,
                b['rect'].width,
                b['rect'].height
            )
            
            # Check if visible
            if (-200 < b_rect.right and b_rect.left < config.WIDTH + 200 and
                -200 < b_rect.bottom and b_rect.top < config.HEIGHT + 200):
                
                # Main building
                pygame.draw.rect(screen, b['color'], b_rect)
                
                # Building outline
                pygame.draw.rect(screen, (50, 50, 50), b_rect, 2)
                
                # Windows (simplified)
                window_color = (255, 255, 150) if not time_system or not time_system.is_night() else (200, 200, 100)
                
                # Draw window grid
                window_size = 10
                spacing = 20
                
                for wx in range(b_rect.x + 15, b_rect.right - 15, spacing):
                    for wy in range(b_rect.y + 15, b_rect.bottom - 15, spacing):
                        if wx + window_size < b_rect.right and wy + window_size < b_rect.bottom:
                            pygame.draw.rect(screen, window_color,
                                           (wx, wy, window_size, window_size), 1)
                            
        # Draw point of interest (police station, etc)
        for poi_key, poi in self.pois.items():
            poi_rect = pygame.Rect(
                poi['x'] - poi['width']//2 - camera.x,
                poi['y'] - poi['height']//2 - camera.y,
                poi['width'],
                poi['height']
            )
            
            if (-200 < poi_rect.right and poi_rect.left < config.WIDTH + 200 and
                -200 < poi_rect.bottom and poi_rect.top < config.HEIGHT + 200):
                
                # Draw police station
                if poi['type'] == 'police_station':
                    pygame.draw.rect(screen, poi['color'], poi_rect)
                    pygame.draw.rect(screen, (100, 150, 200), poi_rect, 3)
                    
                    # Badge/emblem
                    badge_color = (100, 150, 200)
                    pygame.draw.circle(screen, badge_color, (int(poi_rect.centerx), int(poi_rect.centery)), 20)
                    pygame.draw.rect(screen, (200, 200, 200), 
                                   (poi_rect.centerx - 5, poi_rect.centery - 15, 10, 30), 2)
                            
        # Draw street lights
        is_night = time_system and time_system.is_night()
        light_color_day = (100, 100, 100)
        light_color_night = (255, 200, 100)
        light_glow_color = (255, 255, 150)
        
        for light in self.street_lights:
            light_x = light['x'] - camera.x
            light_y = light['y'] - camera.y
            
            # Only draw if visible
            if -50 < light_x < config.WIDTH + 50 and -50 < light_y < config.HEIGHT + 50:
                light_color = light_color_night if is_night else light_color_day
                pole_color = (40, 40, 40)
                
                # Draw pole
                pygame.draw.line(screen, pole_color, (light_x, light_y + 20), (light_x, light_y - 30), 3)
                
                # Draw light bulb
                pygame.draw.circle(screen, light_color, (int(light_x), int(light_y - 30)), 6)
                
                # Draw glow effect at night
                if is_night:
                    glow_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (255, 200, 100, 40), (30, 30), 30)
                    screen.blit(glow_surface, (light_x - 30, light_y - 60))
                            
    def draw_water_border(self, screen, camera):
        """Draw water at edges of map"""
        water_width = config.MAP_BOUNDARY['water_width']
        
        # Draw water border strips
        # Top
        if camera.y < water_width:
            h = min(water_width - camera.y, config.HEIGHT)
            screen.fill(config.COLORS['WATER_DARK'], (0, 0, config.WIDTH, h))
            
        # Bottom
        bottom_water_y = config.WORLD_SIZE - water_width - camera.y
        if bottom_water_y > 0:
            h = min(bottom_water_y, config.HEIGHT)
            screen.fill(config.COLORS['WATER_DARK'], (0, config.HEIGHT - h, config.WIDTH, h))
            
        # Left
        if camera.x < water_width:
            w = min(water_width - camera.x, config.WIDTH)
            screen.fill(config.COLORS['WATER_DARK'], (0, 0, w, config.HEIGHT))
            
        # Right
        right_water_x = config.WORLD_SIZE - water_width - camera.x
        if right_water_x > 0:
            w = min(right_water_x, config.WIDTH)
            screen.fill(config.COLORS['WATER_DARK'], (config.WIDTH - w, 0, w, config.HEIGHT))

