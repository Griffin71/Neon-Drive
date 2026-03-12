# Neon City Drive - Implementation TODO

## Phase 1: Core Systems
- [ ] 1. Update config.py with new settings (graphics, sound, controls, time)
- [ ] 2. Create player.py (player character with on-foot controls)
- [ ] 3. Create weapons.py (guns, machine guns, grenades, fists)
- [ ] 4. Create enemy.py (gangs with AI)

## Phase 2: Vehicle System
- [ ] 5. Update car.py with multiple car types (sports, SUV, truck, etc.)
- [ ] 6. Create vehicle_manager.py (vehicle spawning, switching)

## Phase 3: World System
- [ ] 7. Update world.py (roads, lake, water boundaries, time cycle)
- [ ] 8. Create time system (day/night cycle with 5 sec per hour)

## Phase 4: Menu System
- [ ] 9. Create main_menu.py (New Game, Settings, Load Save, Exit)
- [ ] 10. Create settings_menu.py (Controls, Sound, Graphics divisions)
- [ ] 11. Create in_game_menu.py (Map first, settings, load game)

## Phase 5: Game Systems
- [ ] 12. Create save_system.py (save/load functionality)
- [ ] 13. Create health_system.py (player health, damage)
- [ ] 14. Expand missions to 10 missions
- [ ] 15. Add mini-map HUD

## Phase 6: Integration
- [ ] 16. Rewrite game.py with all new systems
- [ ] 17. Test and fix issues

## Time System
- 5 seconds = 1 game hour (1 minute = 12 game hours)
- Day phases: Midnight, Morning, Midday, Afternoon, Sunset, Night

## World Boundaries
- Map surrounded by water like GTA
- Lake/dam in the middle
- Roads connecting areas

