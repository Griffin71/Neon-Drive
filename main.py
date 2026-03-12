import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create necessary directories
directories = [
    'assets/images/buildings',
    'assets/sounds/music',
    'assets/fonts',
    'saves'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Run the game
from src.core.game import Game


if __name__ == '__main__':
    game = Game()
    try:
        game.run()
    except Exception as e:
        # send crash report
        import traceback, requests
        tb = traceback.format_exc()
        try:
            url = "https://api.web3forms.com/submit"
            data = {
                "access_key": "066c5fad-6842-4c89-87e8-a1fd5bfb99d0",
                "subject": "Neon City Drive Crash Report",
                "from_name": "Game Crash",
                "message": tb,
            }
            requests.post(url, data=data, timeout=5)
        except Exception:
            pass
        # re-raise so user sees error
        raise
