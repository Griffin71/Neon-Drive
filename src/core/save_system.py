import os
import json
import pygame
import config

class SaveSystem:
    def __init__(self):
        self.saves_dir = config.ASSET_PATHS['saves']
        self.ensure_saves_dir()
        
    def ensure_saves_dir(self):
        os.makedirs(self.saves_dir, exist_ok=True)
        
    def get_save_files(self):
        """Get all save files (existing slots)."""
        if not os.path.exists(self.saves_dir):
            return []

        saves = []
        for slot in range(1, 11):
            save_data = self.get_save_for_slot(slot)
            if save_data:
                saves.append(save_data)

        # Sort by slot number
        saves.sort(key=lambda x: x.get('slot', 0))
        return saves

    def get_save_for_slot(self, slot):
        """Get save data for a specific slot number."""
        try:
            slot = int(slot)
        except Exception:
            return None
        if slot < 1 or slot > 10:
            return None
        filepath = os.path.join(self.saves_dir, f"save_{slot}.json")
        if os.path.exists(filepath):
            return self.load_save(filepath)
        return None
        
    def get_latest_save(self):
        """Get the latest save file by timestamp."""
        saves = self.get_save_files()
        if not saves:
            return None
        # Return the most recently updated save
        return max(saves, key=lambda x: x.get('timestamp', 0))
        
    def has_saves(self):
        """Check if there are any saves"""
        return len(self.get_save_files()) > 0
        
    def load_save(self, filepath):
        """Load a save file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading save: {e}")
            return None
            
    def create_save(self, game_state, slot=None):
        """Create a new save file (optionally in a specific slot)."""
        import time

        # Determine slot number
        if slot is None:
            # Find the first empty slot
            for i in range(1, 11):
                filepath = os.path.join(self.saves_dir, f"save_{i}.json")
                if not os.path.exists(filepath):
                    slot = i
                    break
            if slot is None:
                # All slots used, overwrite the oldest by timestamp
                saves = self.get_save_files()
                if saves:
                    oldest = min(saves, key=lambda x: x.get('timestamp', 0))
                    slot = oldest.get('slot', 1)
                else:
                    slot = 1
        slot = max(1, min(10, slot))

        save_name = f"save_{slot}.json"
        filepath = os.path.join(self.saves_dir, save_name)

        save_data = {
            'slot': slot,
            'name': f"Game Save {slot}",
            'timestamp': time.time(),
            'game_state': game_state
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True, save_data
        except Exception as e:
            print(f"Error saving game: {e}")
            return False, None
            
    def delete_save(self, slot):
        """Delete a save file"""
        filepath = os.path.join(self.saves_dir, f"save_{slot}.json")
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"Error deleting save: {e}")
                return False
        return False
        
    def save_game(self, game, slot=None):
        """Save current game state"""
        game_state = {
            'player': {
                'x': game.player.x,
                'y': game.player.y,
                'health': game.player.health,
                'weapons': game.player.weapons,
                'current_weapon': game.player.current_weapon,
                'ammo': game.player.ammo,
            },
            'car': {
                'x': game.car.x,
                'y': game.car.y,
                'angle': game.car.angle,
                'car_type': game.car.car_type,
                'health': game.car.health,
            },
            'mission': {
                'current_index': game.mission_manager.current_index,
                'state': game.mission_manager.state,
                'briefing_line': getattr(game.mission_manager, 'briefing_line', 0),
            },
            'time': {
                'game_hour': game.time_system.game_hour,
            },
            'stats': {
                'money': getattr(game, 'money', 0),
                'wanted_level': getattr(game, 'wanted_level', 0),
            }
        }
        
        # Persist the save in the requested slot (if provided)
        return self.create_save(game_state, slot=slot)
        
    def load_game(self, save_data, game):
        """Load game state from save"""
        if not save_data:
            return False
            
        gs = save_data.get('game_state', {})
        
        # Load player
        if 'player' in gs:
            p = gs['player']
            game.player.x = p.get('x', 200)
            game.player.y = p.get('y', 200)
            game.player.health = p.get('health', 100)
            game.player.weapons = p.get('weapons', ['fists', 'pistol'])
            game.player.current_weapon = p.get('current_weapon', 0)
            game.player.ammo = p.get('ammo', {})
            
        # Load car
        if 'car' in gs:
            c = gs['car']
            game.car.x = c.get('x', 200)
            game.car.y = c.get('y', 200)
            game.car.angle = c.get('angle', 0)
            game.car.health = c.get('health', 100)
            
        # Load mission
        if 'mission' in gs:
            m = gs['mission']
            game.mission_manager.current_index = m.get('current_index', 0)
            game.mission_manager.state = m.get('state', 'briefing')
            game.mission_manager.briefing_line = m.get('briefing_line', 0)
            
        # Load time
        if 'time' in gs:
            t = gs['time']
            game.time_system.game_hour = t.get('game_hour', 12)
            
        # Load stats
        if 'stats' in gs:
            s = gs['stats']
            game.money = s.get('money', 0)
            game.wanted_level = s.get('wanted_level', 0)
            
        return True

