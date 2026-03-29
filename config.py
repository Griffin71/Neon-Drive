# Game settings
WIDTH, HEIGHT = 1024, 768
WORLD_SIZE = 4000
FPS = 60

# Colors
COLORS = {
    'GRASS': (34, 139, 34),
    'DARK_GRASS': (28, 100, 28),
    'BUILDING': (105, 105, 105),
    'BUILDING_DARK': (80, 80, 80),
    'ROAD': (60, 60, 60),
    'ROAD_LINE': (255, 255, 255),
    'WATER': (20, 80, 180),
    'WATER_DARK': (15, 60, 150),
    'LAKE': (30, 100, 200),
    'CAR_BODY': (255, 0, 0),
    'CAR_LINE': (0, 0, 0),
    'TARGET': (255, 255, 0),
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'PURPLE': (128, 0, 128),
    'GRAY': (128, 128, 128),
    'DARK_GRAY': (64, 64, 64),
    'UI_BG': (0, 0, 0, 180),
    'UI_BORDER': (255, 0, 128),
    'HEALTH': (0, 255, 0),
    'HEALTH_LOW': (255, 0, 0),
    # Time colors
    'NIGHT_OVERLAY': (0, 0, 30, 180),
    'SUNSET_OVERLAY': (255, 100, 50, 100),
    'DAY_OVERLAY': (255, 255, 200, 30),
}

# Car physics configurations
CAR_CONFIG = {
    'default': {
        'name': 'Sedan',
        'acceleration': 250.0,
        'drag': 2.0,
        'turn_speed': 180.0,
        'max_speed': 800.0,
        'weight': 1000,
        'color': (200, 50, 50),
        'width': 40,
        'height': 24,
    },
    'sports': {
        'name': 'Sports Car',
        'acceleration': 400.0,
        'drag': 1.5,
        'turn_speed': 220.0,
        'max_speed': 1000.0,
        'weight': 800,
        'color': (255, 0, 0),
        'width': 45,
        'height': 22,
    },
    'suv': {
        'name': 'SUV',
        'acceleration': 180.0,
        'drag': 2.5,
        'turn_speed': 140.0,
        'max_speed': 600.0,
        'weight': 1800,
        'color': (50, 100, 200),
        'width': 50,
        'height': 28,
    },
    'truck': {
        'name': 'Pickup Truck',
        'acceleration': 150.0,
        'drag': 3.0,
        'turn_speed': 120.0,
        'max_speed': 500.0,
        'weight': 2000,
        'color': (139, 69, 19),
        'width': 55,
        'height': 26,
    },
    'supercar': {
        'name': 'Supercar',
        'acceleration': 500.0,
        'drag': 1.2,
        'turn_speed': 250.0,
        'max_speed': 1200.0,
        'weight': 700,
        'color': (255, 255, 0),
        'width': 48,
        'height': 20,
    },
    'motorcycle': {
        'name': 'Motorcycle',
        'acceleration': 300.0,
        'drag': 1.0,
        'turn_speed': 300.0,
        'max_speed': 900.0,
        'weight': 300,
        'color': (50, 50, 50),
        'width': 25,
        'height': 10,
    },
    'taxi': {
        'name': 'Taxi',
        'acceleration': 220.0,
        'drag': 2.2,
        'turn_speed': 170.0,
        'max_speed': 700.0,
        'weight': 1100,
        'color': (255, 215, 0),
        'width': 42,
        'height': 24,
    },
    'police': {
        'name': 'Police Car',
        'acceleration': 350.0,
        'drag': 1.8,
        'turn_speed': 200.0,
        'max_speed': 900.0,
        'weight': 950,
        'color': (20, 20, 60),
        'width': 44,
        'height': 24,
    },
}

# Player configurations
PLAYER_CONFIG = {
    'walking_speed': 150.0,
    'running_speed': 280.0,
    'health': 100,
    'width': 16,
    'height': 32,
}

# Weapon configurations
WEAPONS = {
    'fists': {
        'name': 'Fists',
        'damage': 10,
        'range': 30,
        'cooldown': 0.5,
        'infinite': True,
        'icon': '👊',
    },
    'pistol': {
        'name': 'Pistol',
        'damage': 25,
        'range': 300,
        'cooldown': 0.4,
        'ammo': 12,
        'icon': '🔫',
    },
    'machine_gun': {
        'name': 'Machine Gun',
        'damage': 15,
        'range': 250,
        'cooldown': 0.1,
        'ammo': 30,
        'icon': '🖊️',
    },
    'shotgun': {
        'name': 'Shotgun',
        'damage': 60,
        'range': 100,
        'cooldown': 1.0,
        'ammo': 8,
        'icon': '💥',
    },
    'grenade': {
        'name': 'Grenade',
        'damage': 100,
        'range': 150,
        'cooldown': 2.0,
        'ammo': 5,
        'icon': '💣',
        'explosion_radius': 80,
    },
    'rifle': {
        'name': 'Assault Rifle',
        'damage': 30,
        'range': 400,
        'cooldown': 0.15,
        'ammo': 30,
        'icon': '🔧',
    },
}

# Ammo shop pricing (in Rand)
# Pricing set to 20 Rand per ammo unit as per design.
AMMO_PRICES = {
    'pistol': {'amount': 12, 'price': 12 * 20},
    'shotgun': {'amount': 8, 'price': 8 * 20},
    'machine_gun': {'amount': 30, 'price': 30 * 20},
    'rifle': {'amount': 30, 'price': 30 * 20},
    'grenade': {'amount': 2, 'price': 2 * 20},
}

# Time system (10 seconds = 1 in-game minute)
# (So 1 in-game hour ~= 10 real minutes)
TIME_SCALE = 10  # seconds per in-game minute
TIME_PHASES = {
    'midnight': {'start': 0, 'end': 5, 'name': 'Midnight', 'brightness': 0.1},
    'night': {'start': 5, 'end': 6, 'name': 'Night', 'brightness': 0.2},
    'morning': {'start': 6, 'end': 8, 'name': 'Morning', 'brightness': 0.5},
    'midday': {'start': 8, 'end': 16, 'name': 'Midday', 'brightness': 1.0},
    'afternoon': {'start': 16, 'end': 18, 'name': 'Afternoon', 'brightness': 0.8},
    'sunset': {'start': 18, 'end': 20, 'name': 'Sunset', 'brightness': 0.4},
    'evening': {'start': 20, 'end': 22, 'name': 'Evening', 'brightness': 0.3},
}

# Graphics settings
GRAPHICS_SETTINGS = {
    'resolutions': [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1920, 1080),
    ],
    'screen_types': ['fullscreen', 'windowed', 'borderless'],
    'default': {
        'resolution': (1024, 768),
        'screen_type': 'fullscreen',
        'vsync': True,
    }
}

# Sound settings
SOUND_SETTINGS = {
    'default': {
        'music_volume': 0.5,
        'sfx_volume': 0.7,
        'radio_volume': 0.6,
    }
}

# Control mappings
CONTROLS = {
    'vehicle': {
        'name': 'In Vehicle',
        'accelerate': 'W',
        'brake': 'S',
        'turn_left': 'A',
        'turn_right': 'D',
        'horn': 'H',
        'exit': 'F',
    },
    'on_foot': {
        'name': 'On Foot',
        'move_forward': 'W',
        'move_back': 'S',
        'turn_left': 'A',
        'turn_right': 'D',
        'run': 'SHIFT',
        'jump': 'SPACE',
        'enter_vehicle': 'F',
        'attack': 'LEFT MOUSE',
        'aim': 'RIGHT MOUSE',
        'reload': 'R',
        'weapon_1': '1',
        'weapon_2': '2',
        'weapon_3': '3',
        'weapon_4': '4',
        'weapon_5': '5',
        'grenade': 'G',
        'cycle_weapon': 'Q',
    },
    'general': {
        'name': 'General',
        'menu': 'ESC',
        'map': 'M',
        'journal': 'J',
    }
}

# Asset paths
ASSET_PATHS = {
    'images': 'assets/images/',
    'images_buildings': 'assets/images/buildings/',
    'images_ui': 'assets/images/ui/',
    'sounds': 'assets/sounds/',
    'sounds_music': 'assets/sounds/music/',
    'fonts': 'assets/fonts/',
    'saves': 'saves/'
}

# Map boundaries
MAP_BOUNDARY = {
    'water_width': 100,
}

# World points of interest (in world coordinates)
LOCATIONS = {
    'safe_house': (600, 2400),
    'hospital': (650, 2450),
    'gang_house': (800, 2000),
    'ammo_store': (2500, 1200),
    'police_station': (3500, 3500),
}

# UI/Gameplay
CURRENCY_SYMBOL = 'R'

# Mission configurations
MISSION_COUNT = 20

