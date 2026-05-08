"""Datei-Controller: Lesen, Schreiben, Suchen, Löschen (Papierkorb), Safe-Path-Check."""
import os, shutil, glob
from pathlib import Path
from send2trash import send2trash
from core.logger import get_logger

logger = get_logger("FileController")

def _safe_path(path: str) -> Path:
    p = Path(path).resolve()
    # Verhindere Zugriff auf sensible Systemverzeichnisse
    forbidden = ["C:\\Windows", "C:\\Program Files", "/etc", "/usr", "/bin", "/sbin", "/sys", "/proc"]
    for f in forbidden:
        if str(p).startswith(f):
            raise PermissionError(f"Zugriff auf {f} nicht erlaubt.")
    return p

def file_controller(parameters=None, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    path = params.get("path", "")
    content = params.get("content", "")

    if player:
        try: player.write_log(f"[File] {action} {path}")
        except: pass

    try:
        if action == "read":
            p = _safe_path(path)
            if not p.exists(): return f"❌ Datei nicht gefunden: {path}"
            text = p.read_text(encoding="utf-8", errors="ignore")
            return text[:2000] + ("\n... [gekuerzt]" if len(text) > 2000 else "")

        elif action == "write":
            p = _safe_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"✅ Datei geschrieben: {path}"

        elif action == "list":
            p = _safe_path(path) if path else Path(".")
            if not p.exists(): return f"❌ Pfad nicht gefunden: {path}"
            items = list(p.iterdir())
            lines = [f"📁 {p.absolute()}", "=" * 40]
            for item in sorted(items):
                icon = "📁" if item.is_dir() else "📄"
                size = f"({item.stat().st_size} bytes)" if item.is_file() else ""
                lines.append(f"{icon} {item.name} {size}")
            return "\n".join(lines)

        elif action == "search":
            query = params.get("query", "")
            p = _safe_path(path) if path else Path(".")
            matches = list(p.glob(f"**/*{query}*"))
            lines = [f"🔍 Suche nach '{query}' in {p}:", "=" * 40]
            for m in matches[:50]:
                lines.append(f"  {m}")
            return "\n".join(lines)

        elif action == "delete":
            p = _safe_path(path)
            if not p.exists(): return f"❌ Datei nicht gefunden: {path}"
            send2trash(str(p))
            return f"🗑️ In Papierkorb verschoben: {path}"

        else:
            return f"❌ Unbekannte Aktion: '{action}'. Verfuegbar: read, write, list, search, delete"

    except PermissionError as e:
        return f"🛡️ Zugriff verweigert: {e}"
    except Exception as e:
        return f"❌ Fehler: {e}"
