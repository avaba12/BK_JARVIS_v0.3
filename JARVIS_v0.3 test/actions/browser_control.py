import subprocess, platform, os
from memory.config_manager import ConfigManager

_OS = platform.system()

def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url: return "about:blank"
    if "://" in url: return url
    if "." not in url: url = url + ".com"
    return "https://" + url

def _is_allowed_url(url: str) -> bool:
    cfg = ConfigManager()
    allowed = cfg.get("allowed_urls", [])
    if not allowed: return True
    url_lower = url.lower()
    for allowed_url in allowed:
        if allowed_url.lower() in url_lower: return True
    return False

def browser_control(parameters=None, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    url = params.get("url", "")
    if player:
        try: player.write_log(f"[Browser] {action} {url}")
        except: pass
    try:
        if action == "go_to":
            url = _normalize_url(url)
            if not _is_allowed_url(url):
                return f"❌ URL '{url}' ist nicht in der erlaubten Liste. Fuege sie in Einstellungen > Sicherheit hinzu."

            # FIX: os.startfile() ist auf Windows zuverlaessiger als subprocess
            if _OS == "Windows":
                os.startfile(url)
            elif _OS == "Darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
            return f"✅ Geoeffnet: {url}"

        elif action == "search":
            query = params.get("query", "")
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            return browser_control({"action": "go_to", "url": search_url}, player=player)
        else:
            return f"❌ Unbekannte Browser-Aktion: '{action}'"
    except Exception as e:
        return f"❌ Browser-Fehler: {e}"
