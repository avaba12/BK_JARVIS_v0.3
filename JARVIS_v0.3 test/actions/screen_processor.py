"""Screenshot mit mss fuer Vision-Analyse."""
import tempfile
from pathlib import Path
from core.logger import get_logger

logger = get_logger("Screen")

def screen_processor(parameters=None, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if player:
        try: player.write_log(f"[Screen] {action}")
        except: pass

    try:
        if action == "screenshot":
            import mss
            import mss.tools
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Hauptmonitor
                screenshot = sct.grab(monitor)
                output = "screenshot.png"
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=output)
                return f"✅ Screenshot gespeichert: {output}"
        else:
            return f"❌ Unbekannte Aktion: '{action}'"
    except Exception as e:
        return f"❌ Screenshot-Fehler: {e}"
