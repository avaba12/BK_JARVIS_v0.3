"""Reminder-System mit lokalen Timern."""
import threading, time
from datetime import datetime, timedelta
from core.logger import get_logger

logger = get_logger("Reminder")

_active_reminders = {}
_reminder_counter = 0
_reminder_lock = threading.Lock()

def _parse_time(time_str: str) -> int:
    time_str = time_str.strip().lower()
    if ":" in time_str:
        try:
            target = datetime.strptime(time_str, "%H:%M")
            now = datetime.now()
            target = target.replace(year=now.year, month=now.month, day=now.day)
            if target < now:
                target += timedelta(days=1)
            return int((target - now).total_seconds())
        except ValueError:
            pass
    if time_str.endswith("s"): return int(time_str[:-1])
    elif time_str.endswith("m"): return int(time_str[:-1]) * 60
    elif time_str.endswith("h"): return int(time_str[:-1]) * 3600
    elif time_str.endswith("d"): return int(time_str[:-1]) * 86400
    try: return int(time_str)
    except ValueError: return 300

def _reminder_thread(reminder_id: int, delay: int, text: str, callback=None):
    time.sleep(delay)
    with _reminder_lock:
        if reminder_id not in _active_reminders: return
        del _active_reminders[reminder_id]
    msg = f"🔔 REMINDER: {text}"
    logger.info(msg)
    if callback:
        try: callback(msg)
        except: pass

def reminder(parameters=None, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    text = params.get("text", "").strip()
    time_str = params.get("time", "").strip()
    if not text: return "❌ Kein Reminder-Text angegeben."
    if not time_str: return "❌ Keine Zeit angegeben. Beispiele: '5m', '1h', '14:30'"
    delay = _parse_time(time_str)
    if delay <= 0: return "❌ Zeit liegt in der Vergangenheit."
    global _reminder_counter
    with _reminder_lock:
        _reminder_counter += 1
        reminder_id = _reminder_counter
        _active_reminders[reminder_id] = {"text": text, "delay": delay, "created": time.time()}
    t = threading.Thread(target=_reminder_thread, args=(reminder_id, delay, text,
        lambda msg: player.write_log(msg) if player else None), daemon=True, name=f"Reminder-{reminder_id}")
    t.start()
    when = datetime.now() + timedelta(seconds=delay)
    return f"✅ Reminder gesetzt: '{text}' in {delay}s (um {when.strftime('%H:%M:%S')}). Aktive: {len(_active_reminders)}"

def list_reminders(parameters=None, response=None, player=None, session_memory=None) -> str:
    with _reminder_lock:
        if not _active_reminders: return "ℹ️ Keine aktiven Reminder."
        lines = [f"📋 Aktive Reminder ({len(_active_reminders)}):", "=" * 40]
        for rid, info in _active_reminders.items():
            remaining = max(0, int(info["delay"] - (time.time() - info["created"])))
            lines.append(f"  #{rid}: '{info['text']}' — noch {remaining}s")
        return "\n".join(lines)

def cancel_reminder(parameters=None, response=None, player=None, session_memory=None) -> str:
    params = parameters or {}
    reminder_id = params.get("id", 0)
    with _reminder_lock:
        if reminder_id in _active_reminders:
            del _active_reminders[reminder_id]
            return f"✅ Reminder #{reminder_id} abgebrochen."
        return f"❌ Reminder #{reminder_id} nicht gefunden."
