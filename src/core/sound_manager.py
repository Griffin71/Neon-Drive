import os
import pygame
import config


class SoundManager:
    def __init__(self):
        # Initialize mixer if not already
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.sfx = {}
        self.music_channel = None
        self.ambient_channel = None
        self._load_sounds()

    def _load_sounds(self):
        # SFX folder is under assets/sounds/sfx
        sfx_dir = os.path.join(config.ASSET_PATHS['sounds'], 'sfx')
        if not os.path.isdir(sfx_dir):
            return

        for filename in os.listdir(sfx_dir):
            if not filename.lower().endswith(('.wav', '.mp3', '.ogg')):
                continue
            key = os.path.splitext(filename)[0]
            path = os.path.join(sfx_dir, filename)
            try:
                self.sfx[key] = pygame.mixer.Sound(path)
            except Exception:
                pass

    def play_sfx(self, key, volume=1.0):
        snd = self.sfx.get(key)
        if not snd:
            return
        try:
            snd.set_volume(volume)
            snd.play()
        except Exception:
            pass

    def play_music(self, key, loops=-1, volume=1.0):
        snd = self.sfx.get(key)
        if not snd:
            return
        try:
            # Use dedicated music channel (channel 0) to avoid interrupting sfx
            if self.music_channel is None:
                self.music_channel = pygame.mixer.Channel(0)
            self.music_channel.set_volume(volume)
            self.music_channel.play(snd, loops=loops)
        except Exception:
            pass

    def stop_music(self):
        if self.music_channel:
            try:
                self.music_channel.stop()
            except Exception:
                pass

    def play_ambient(self, key, loops=-1, volume=0.7):
        snd = self.sfx.get(key)
        if not snd:
            return
        try:
            if self.ambient_channel is None:
                self.ambient_channel = pygame.mixer.Channel(1)
            self.ambient_channel.set_volume(volume)
            if not self.ambient_channel.get_busy():
                self.ambient_channel.play(snd, loops=loops)
        except Exception:
            pass

    def stop_ambient(self):
        if self.ambient_channel:
            try:
                self.ambient_channel.stop()
            except Exception:
                pass
