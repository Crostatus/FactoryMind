import os
import datetime

# === COLOR DEFINITIONS ===
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    GREY = "\033[38;5;240m"
    LIGHT_GREY = "\033[38;5;250m"
    ORANGE = "\033[38;5;208m"

def color_text(text: str, color: str, bold: bool = False) -> str:
    return f"{Color.BOLD if bold else ''}{color}{text}{Color.RESET}"


# === LOGGER CLASS ===
class Logger:
    def __init__(self):
        # Load flags from environment (default: True)
        self.debug_enabled = os.getenv("DEBUG", "1") == "1"
        self.trace_enabled = os.getenv("TRACE", "1") == "1"
        self.info_enabled = os.getenv("INFO", "1") == "1"
        self.timestamp_enabled = os.getenv("TIMESTAMP", "1") == "1"

    # internal helper
    def _prefix(self, level: str, color: str, bold=False) -> str:
        prefix = color_text(f"[{level}]", color, bold)
        if self.timestamp_enabled:
            now = datetime.datetime.now().strftime("%H:%M:%S")
            return f"{color_text(now, Color.LIGHT_GREY)} {prefix}"
        return prefix

    def info(self, msg: str):
        if self.info_enabled:
            print(f"{self._prefix('INFO', Color.CYAN)}  {msg}")

    def success(self, msg: str):
        print(f"{self._prefix('OK', Color.GREEN)}    {msg}")

    def warn(self, msg: str):
        print(f"{self._prefix('WARN', Color.ORANGE)}  {msg}")

    def error(self, msg: str):
        print(f"{self._prefix('ERROR', Color.RED, bold=True)} {msg}")

    def debug(self, msg: str):
        if self.debug_enabled:
            print(f"{self._prefix('DEBUG', Color.YELLOW)} {msg}")

    def trace(self, msg: str):
        if self.trace_enabled:
            print(f"{self._prefix('TRACE', Color.GREY)} {color_text(msg, Color.LIGHT_GREY)}")

# === GLOBAL LOGGER INSTANCE ===
log = Logger()