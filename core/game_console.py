from datetime import datetime

from core import game_globals


#=====================================================================
# GameConsole - Debug Logger
#=====================================================================

class GameConsole:
    """
    Simple console logger for debugging.
    Outputs timestamped messages only if debug mode is active.
    """

    @staticmethod
    def log(message: str) -> None:
        """
        Logs a timestamped message to the console if debug mode is enabled.
        
        Args:
            message (str): Message to be logged.
        """
        if game_globals.debug:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")
