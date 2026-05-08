"""Keyword-basierter Planner fuer Apps, Suche, Dateien, Screenshots."""
import re

class Planner:
    def __init__(self):
        pass

    def plan(self, user_input: str) -> dict:
        text = user_input.lower().strip()

        # Browser / Web
        if any(kw in text for kw in ["gehe zu", "gehe auf", "go to", "browse", "öffne die seite", "öffne die website", "oeffne die seite"]):
            url = re.sub(r".*?(gehe zu|gehe auf|go to|browse|öffne die seite|öffne die website|oeffne die seite)\s+", "", text, flags=re.IGNORECASE).strip()
            # Entferne Satzzeichen am Ende
            url = re.sub(r"[.!?]+$", "", url)
            return {"tool": "browser_control", "params": {"action": "go_to", "url": url}}

        # Web-Suche
        if any(kw in text for kw in ["suche nach", "google nach", "finde", "suche"]):
            query = re.sub(r".*?(suche nach|google nach|finde|suche)\s+", "", text, flags=re.IGNORECASE).strip()
            query = re.sub(r"[.!?]+$", "", query)
            return {"tool": "web_search", "params": {"query": query, "mode": "search"}}

        # Apps oeffnen
        if any(kw in text for kw in ["öffne", "open", "starte", "launch", "oeffne"]):
            app_name = re.sub(r".*?(öffne|open|starte|launch|oeffne)\s+", "", text, flags=re.IGNORECASE).strip()
            app_name = re.sub(r"[.!?]+$", "", app_name)
            return {"tool": "open_app", "params": {"app_name": app_name}}

        # Systemsteuerung
        if any(kw in text for kw in ["lautstaerke", "volume", "mute", "stumm", "desktop", "sperren", "screenshot", "bildschirmfoto"]):
            action_map = {
                "lauter": "volume_up", "louder": "volume_up", "volume up": "volume_up",
                "leiser": "volume_down", "quieter": "volume_down", "volume down": "volume_down",
                "stumm": "mute", "mute": "mute",
                "desktop": "show_desktop", "sperren": "lock_screen", "lock": "lock_screen",
                "screenshot": "screenshot", "bildschirmfoto": "screenshot",
            }
            for kw, action in action_map.items():
                if kw in text:
                    return {"tool": "computer_settings", "params": {"action": action}}
            return {"tool": "computer_settings", "params": {"action": "screenshot"}}

        # Reminder
        if any(kw in text for kw in ["erinnere mich", "reminder", "timer", "in 5 minuten", "in 10 minuten"]):
            return {"tool": "reminder", "params": {"text": user_input, "time": "5m"}}

        # Screenshots
        if any(kw in text for kw in ["screenshot", "bildschirm", "foto machen"]):
            return {"tool": "screen_processor", "params": {"action": "screenshot"}}

        # Datei-Operationen
        if any(kw in text for kw in ["datei", "file", "ordner", "folder", "loesche", "delete"]):
            return {"tool": "file_controller", "params": {"action": "list", "path": "."}}

        # ComfyUI
        if any(kw in text for kw in ["bild generieren", "generate image", "comfyui", "bild erstellen"]):
            return {"tool": "comfyui", "params": {"action": "generate", "prompt": user_input}}

        # Home Assistant
        if any(kw in text for kw in ["licht", "lampe", "heizung", "thermostat", "smart home"]):
            return {"tool": "home_assistant", "params": {"action": "list_entities"}}

        # Default: Web-Suche als Fallback
        return {"tool": "web_search", "params": {"query": user_input, "mode": "search"}}
