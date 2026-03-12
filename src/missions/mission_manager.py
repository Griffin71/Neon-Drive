import math
import pygame
import config

class MissionManager:
    """Handles mission progression, objectives, and mission messaging."""

    def __init__(self):
        self.missions = self._create_missions()
        self.current_index = 0
        self.state = 'briefing'  # briefing, active, returning, idle, finished, failed
        self.briefing_line = 0

        # Timers for mission complete / fail messages
        self.complete_timer = 0.0
        self.fail_timer = 0.0
        self.fail_reason = ''

        # Keep the last mission reward (for display/analytics)
        self.last_reward = 0

        # Start with the first briefing ready
        self._start_briefing()

    def _create_missions(self):
        # Mission coordinates are approximate points in the world.
        return [
            {
                'id': 1,
                'title': 'The Burner Run',
                'briefing': [
                    ('Recruiter (phone)', 'Kael Voss… you owe us big. First job’s simple. Prove you can drive.'),
                    ('Recruiter', 'Take this burner phone to the docks. Don’t look inside.')
                ],
                'objective': 'Deliver the burner phone to the docks.',
                'target': (1200, 900),
                'reward': 0,
            },
            {
                'id': 2,
                'title': 'Turf Reclaim',
                'briefing': [
                    ('Recruiter', 'Street thugs stole our shipment. Take it back — fists or wheels.'),
                    ('Thug Boss (dying)', 'LTS owns everything…'),
                    ('Recruiter', 'Good. Drive back to the LTS Gang House for your cut.')
                ],
                'objective': 'Recover the shipment and return to the safe house.',
                'target': (900, 1700),
                'reward': 0,
            },
            {
                'id': 3,
                'title': 'Midnight Medicine',
                'briefing': [
                    ('Recruiter', 'Deliver this “medicine” to the east-side clinic. No detours.'),
                    ('Clinic Owner', 'Tell your boss we’re even.'),
                    ('Recruiter', 'Head home, Shadow. More work waiting.')
                ],
                'objective': 'Deliver the package to the east-side clinic.',
                'target': (2600, 1800),
                'reward': 8500,
            },
            {
                'id': 4,
                'title': 'Lose the Heat',
                'briefing': [
                    ('Recruiter', 'Cops are on us. Lose the tail and dump the evidence in the river.'),
                    ('Recruiter', 'Nice moves. Safe house — now.')
                ],
                'objective': 'Lose the police tail and reach the rendezvous point.',
                'target': (2100, 1200),
                'reward': 12000,
            },
            {
                'id': 5,
                'title': 'Rival Challenge',
                'briefing': [
                    ('Rival Leader (radio)', 'LTS thinks they own these streets? Come take my turf if you’re man enough.'),
                    ('Rival', 'You’re just a pawn…'),
                    ('Recruiter', 'Back to base for the real money.')
                ],
                'objective': 'Take the rival turf. Show them who owns the streets.',
                'target': (1800, 800),
                'reward': 18000,
            },
            {
                'id': 6,
                'title': 'Casino Heist Wheels',
                'briefing': [
                    ('Recruiter', 'Steal the red Banshee from the casino lot and stash it in our garage.'),
                    ('Recruiter', 'Parked. Return to safe house for the next score.')
                ],
                'objective': 'Steal the red Banshee and bring it to the garage.',
                'target': (2400, 700),
                'reward': 25000,
            },
            {
                'id': 7,
                'title': 'ATM Convoy',
                'briefing': [
                    ('Recruiter', 'Rob the downtown ATM truck. Make it quick.'),
                    ('Recruiter', 'Cash secured. Safe house — debrief.')
                ],
                'objective': 'Intercept the ATM caravan and secure the cash.',
                'target': (1500, 1500),
                'reward': 35000,
            },
            {
                'id': 8,
                'title': 'Snitch Elimination',
                'briefing': [
                    ('LTS Boss', 'There’s a snitch at the old warehouse. Make him quiet.'),
                    ('Snitch', 'The boss is selling you out…'),
                    ('Boss', 'Ignore him. Back to the safe house.')
                ],
                'objective': 'Reach the old warehouse and deal with the snitch.',
                'target': (2800, 900),
                'reward': 45000,
            },
            {
                'id': 9,
                'title': 'Mayor’s Briefcase',
                'briefing': [
                    ('LTS Boss', 'Deliver this briefcase to the mayor’s mansion. No questions.'),
                    ('Mayor', 'LTS has our deal.'),
                    ('Boss', 'Safe house. Next level.')
                ],
                'objective': 'Bring the briefcase to the mayor’s mansion.',
                'target': (3200, 1400),
                'reward': 55000,
            },
            {
                'id': 10,
                'title': 'West Side Race',
                'briefing': [
                    ('Rival (radio)', 'You killed my brother. Race me for the west side — winner takes all.'),
                    ('Rival', 'They’ll betray you too…'),
                    ('Recruiter', 'Victory lap back to base.')
                ],
                'objective': 'Win the west side street race.',
                'target': (1800, 2400),
                'reward': 75000,
            },
            {
                'id': 11,
                'title': 'Highway Hijack',
                'briefing': [
                    ('LTS Boss', 'Hijack the armored truck on highway 7.'),
                    ('Truck Driver', 'Big mistake, kid…'),
                    ('Boss', 'Stash it and return to the safe house.')
                ],
                'objective': 'Hijack the armored truck on highway 7.',
                'target': (2400, 2200),
                'reward': 95000,
            },
            {
                'id': 12,
                'title': 'Underground Stash',
                'briefing': [
                    ('LTS Boss', 'Lose the cops and hide the truck in our underground garage.'),
                    ('Boss', 'You’re my best. Safe house for the next one.')
                ],
                'objective': 'Lose pursuit and stash the truck in the underground garage.',
                'target': (2600, 2000),
                'reward': 110000,
            },
            {
                'id': 13,
                'title': 'Bomb Delivery',
                'briefing': [
                    ('Recruiter (worried)', 'Boss wants you to plant this at rival HQ. Do it.'),
                    ('Rival Guard', 'LTS is finished…'),
                    ('Recruiter', 'Back to base — we need to talk.')
                ],
                'objective': 'Deliver the bomb to the rival HQ.',
                'target': (2000, 1200),
                'reward': 130000,
            },
            {
                'id': 14,
                'title': 'Council Intimidation',
                'briefing': [
                    ('LTS Boss', 'Scare the three council members tonight. Make them vote our way.'),
                    ('Council Member 3', 'Real power is coming for you…'),
                    ('Boss', 'Safe house. Good work.')
                ],
                'objective': 'Reach all three council members and intimidate them.',
                'target': (2200, 1600),
                'reward': 150000,
            },
            {
                'id': 15,
                'title': 'Traitor Hunt',
                'briefing': [
                    ('Recruiter (secret)', 'There’s a traitor inside our walls. Find him.'),
                    ('Traitor', 'Boss is selling us to the feds!'),
                    ('Recruiter', 'Get back here — we have to move fast.')
                ],
                'objective': 'Find the traitor and confront them.',
                'target': (2100, 1300),
                'reward': 180000,
            },
            {
                'id': 16,
                'title': 'Central Bank Vault',
                'briefing': [
                    ('LTS Boss (angry)', 'Rob the central bank vault. Prove your loyalty.'),
                    ('Bank Manager', 'You won’t get away with this…'),
                    ('Boss', 'Back to the safe house.')
                ],
                'objective': 'Reach the central bank and secure the vault.',
                'target': (2800, 2000),
                'reward': 250000,
            },
            {
                'id': 17,
                'title': 'Lighthouse Truth',
                'briefing': [
                    ('Recruiter (secret call)', 'Boss is lying. Meet me at the old lighthouse — I have proof.'),
                    ('Recruiter', 'He’s framing you. Come back to base.')
                ],
                'objective': 'Meet the recruiter at the old lighthouse.',
                'target': (600, 800),
                'reward': 200000,
            },
            {
                'id': 18,
                'title': 'Tower Trap',
                'briefing': [
                    ('LTS Boss (final call)', 'Bring the proof to the LTS tower… or die.'),
                    ('Boss (ambush)', 'You were useful… until now.'),
                    ('Recruiter', 'He’s gone rogue — get back here!')
                ],
                'objective': 'Reach the LTS tower and survive the ambush.',
                'target': (3200, 2200),
                'reward': 300000,
            },
            {
                'id': 19,
                'title': 'Neon Reckoning',
                'briefing': [
                    ('Recruiter', 'Take the fight straight to the LTS tower. I’ve got your back from the streets.'),
                    ('LTS Boss (final fight)', 'You think you can run my city?!')
                ],
                'objective': 'Storm the LTS tower and take down the boss.',
                'target': (3200, 2200),
                'reward': 500000,
            },
            {
                'id': 20,
                'title': 'Neon Shadow’s Choice',
                'briefing': [
                    ('Recruiter', 'It’s over, Kael. The syndicate is finished. The city is yours — keep it or burn it down?'),
                    ('Narration', 'You did it. Neon City is finally free. The lights belong to the streets now.')
                ],
                'objective': 'Decide the fate of Neon City.',
                'target': None,
                'reward': 1000000,
            },
        ]

    def _start_briefing(self):
        self.state = 'briefing'
        self.briefing_line = 0
        self.complete_timer = 0.0
        self.fail_timer = 0.0

    def get_current_mission(self):
        if self.state == 'finished' or self.current_index >= len(self.missions):
            return None
        if self.state == 'returning':
            return {
                'title': 'Return to Safe House',
                'objective': 'Return to the LTS Safe House for your next briefing.',
                'target': config.LOCATIONS.get('safe_house')
            }
        if self.state == 'idle':
            # While waiting at the safe house, show the next mission info
            return self.missions[self.current_index]
        return self.missions[self.current_index]

    def get_display_text(self):
        # Display the mission objective or briefing text
        if self.state == 'briefing':
            mission = self.get_current_mission()
            if not mission:
                return ''
            lines = []
            briefing = mission.get('briefing', [])
            if self.briefing_line < len(briefing):
                speaker, text = briefing[self.briefing_line]
                lines.append(f"{speaker}:")
                lines.append(text)
                lines.append('(Press SPACE to continue)')
            return '\n'.join(lines)

        if self.state == 'active':
            mission = self.get_current_mission()
            if not mission:
                return ''
            return f"{mission.get('title')} - {mission.get('objective')}"

        if self.state == 'returning':
            return 'MISSION COMPLETE! Return to the safe house for your next briefing.'

        if self.state == 'idle':
            mission = self.get_current_mission()
            if not mission:
                return ''
            return f"You are back at the safe house. Press SPACE to receive your next mission: {mission.get('title')}"

        if self.state == 'finished':
            return 'All missions complete. The city is yours.'

        return ''

    def advance_briefing(self, game=None):
        """Advance briefing dialogue. When it ends, start the mission."""
        # If we're waiting at the safe house, start the next mission briefing
        if self.state == 'idle':
            self._start_briefing()
            return

        mission = self.get_current_mission()
        if not mission:
            return

        briefing = mission.get('briefing', [])
        if self.briefing_line < len(briefing) - 1:
            self.briefing_line += 1
            return

        # End of briefing — start mission
        self.state = 'active'
        self.briefing_line = 0
        # If this is the final mission with no target, immediately complete
        if mission.get('target') is None:
            self._complete_mission(game)

    def update(self, player, game, dt):
        # Handle timers
        if self.complete_timer > 0:
            self.complete_timer -= dt
            if self.complete_timer <= 0:
                self.complete_timer = 0
                # After mission completion message, remain in returning state until player reaches safe house
                # After mission failure message, allow retry
                if self.state == 'failed':
                    self.state = 'active'
                return

        if self.fail_timer > 0:
            self.fail_timer -= dt
            if self.fail_timer <= 0:
                self.fail_timer = 0
                self.state = 'active'
            return

        # If mission is finished, nothing else to do
        if self.state == 'finished':
            return

        # If waiting for briefing (player must return to safe house to start next mission)
        if self.state == 'idle':
            # If player reaches safe house, trigger briefing
            sx, sy = config.LOCATIONS.get('safe_house', (0, 0))
            dist = math.hypot(player.x - sx, player.y - sy)
            if dist < 120:
                self._start_briefing()
            return

        # Active mission tracking
        if self.state == 'active':
            mission = self.get_current_mission()
            if not mission:
                return
            if mission.get('target') is None:
                # No objective location (final story mission) - complete immediately
                self._complete_mission(game)
                return

            tx, ty = mission.get('target')
            dist = math.hypot(player.x - tx, player.y - ty)
            if dist < 120:
                self._complete_mission(game)
            return

        # Returning to safe house after completion
        if self.state == 'returning':
            sx, sy = config.LOCATIONS.get('safe_house', (0, 0))
            dist = math.hypot(player.x - sx, player.y - sy)
            if dist < 120:
                # Move to next mission (but wait for player to accept it)
                self.current_index += 1
                if self.current_index >= len(self.missions):
                    self.state = 'finished'
                    game.hud.show_temporary_message('ALL MISSIONS COMPLETE', '', (0, 255, 0), 7.0)
                    return

                # Wait for player to press SPACE at safe house to start next briefing
                self.state = 'idle'
                self.briefing_line = 0
                if hasattr(game, 'hud'):
                    game.hud.show_temporary_message('Back at the safe house. Press SPACE for the next mission.', '', (255, 255, 255), 5.0)
            return

    def _complete_mission(self, game):
        mission = self.get_current_mission()
        if not mission:
            return

        reward = mission.get('reward', 0)
        self.last_reward = reward
        if reward and hasattr(game, 'money'):
            game.money += reward
        # Play sound and show message
        if hasattr(game, 'hud'):
            game.hud.show_temporary_message('MISSION COMPLETE!', 'Return to the LTS Safe House for your next briefing.', (0, 255, 0), duration=7.0)
        if hasattr(game, 'sound_manager'):
            game.sound_manager.play_sfx('mission_passed')

        self.state = 'returning'
        self.complete_timer = 7.0

    def fail_mission(self, reason, game=None):
        self.state = 'failed'
        self.fail_reason = reason
        self.fail_timer = 7.0
        if hasattr(game, 'hud'):
            game.hud.show_temporary_message('MISSION FAILED', reason, (255, 0, 0), duration=7.0)
        if hasattr(game, 'sound_manager'):
            game.sound_manager.play_sfx('mission_failed')

    def draw_target(self, screen, camera):
        if self.state in ['finished', 'idle', 'briefing']:
            return

        mission = self.get_current_mission()
        if not mission or not mission.get('target'):
            return

        tx, ty = mission['target']
        marker_x = tx - camera.x
        marker_y = ty - camera.y

        if -50 < marker_x < config.WIDTH + 50 and -50 < marker_y < config.HEIGHT + 50:
            pygame.draw.circle(screen, config.COLORS['TARGET'], (int(marker_x), int(marker_y)), 25)
            pygame.draw.circle(screen, config.COLORS['BLACK'], (int(marker_x), int(marker_y)), 25, 3)
