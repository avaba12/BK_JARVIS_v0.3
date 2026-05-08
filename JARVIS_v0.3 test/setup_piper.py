"""Piper TTS automatisch herunterladen und einrichten."""
import os, urllib.request, zipfile, shutil, sys, json
from pathlib import Path

def download_file(url, dest, desc=""):
    print(f"  📥 Lade {desc}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as response:
            with open(dest, 'wb') as f:
                f.write(response.read())
        print(f"  ✅ {desc} fertig")
        return True
    except Exception as e:
        print(f"  ❌ Fehler bei {desc}: {e}")
        return False

def setup_piper():
    base = Path("models/piper")
    base.mkdir(parents=True, exist_ok=True)

    # Pruefe ob Piper schon vollstaendig installiert ist
    exe = base / "piper.exe"
    has_model = any(base.glob("*.onnx"))
    has_json = any(base.glob("*.json"))

    if exe.exists() and has_model and has_json:
        print("[OK] Piper TTS ist bereits vollstaendig installiert.")
        return 0

    print("[INFO] Piper TTS wird installiert...")

    # 1. Lade Piper Windows Binary
    if not exe.exists():
        # Versuche verschiedene URLs
        piper_urls = [
            "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip",
            "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_windows_amd64.zip",
        ]
        zip_path = base / "piper.zip"
        downloaded = False
        for url in piper_urls:
            if download_file(url, str(zip_path), "Piper Binary"):
                downloaded = True
                break

        if downloaded and zip_path.exists():
            print("  📦 Entpacke Piper...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(str(base))
                zip_path.unlink(missing_ok=True)
                # Verschiebe Dateien aus Unterordner
                for sub in base.iterdir():
                    if sub.is_dir() and sub.name not in ["__pycache__", "espeak-ng-data"]:
                        for f in sub.iterdir():
                            target = base / f.name
                            if f.is_file():
                                if target.exists():
                                    target.unlink()
                                shutil.move(str(f), str(target))
                        # Verschiebe auch espeak-ng-data falls vorhanden
                        espeak_src = sub / "espeak-ng-data"
                        if espeak_src.exists():
                            espeak_dst = base / "espeak-ng-data"
                            if espeak_dst.exists():
                                shutil.rmtree(str(espeak_dst))
                            shutil.move(str(espeak_src), str(espeak_dst))
                        sub.rmdir()
                print("  ✅ Piper entpackt")
            except Exception as e:
                print(f"  ⚠️ Fehler beim Entpacken: {e}")

    # 2. Lade deutsches Modell (thorsten-de-medium)
    model_name = "thorsten-de-medium"
    model_file = base / f"{model_name}.onnx"
    json_file = base / f"{model_name}.json"

    if not model_file.exists() or not json_file.exists():
        print(f"[INFO] Lade Modell {model_name}...")

        # HuggingFace URLs
        hf_base = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/medium/"

        urls = {
            model_file: [
                hf_base + f"{model_name}.onnx",
                f"https://github.com/rhasspy/piper/releases/download/v1.2.0/{model_name}.onnx",
            ],
            json_file: [
                hf_base + f"{model_name}.onnx.json",
                f"https://github.com/rhasspy/piper/releases/download/v1.2.0/{model_name}.onnx.json",
            ]
        }

        for dest_file, url_list in urls.items():
            if not dest_file.exists():
                for url in url_list:
                    if download_file(url, str(dest_file), dest_file.name):
                        break

    # Pruefe Ergebnis
    exe = base / "piper.exe"
    has_model = any(base.glob("*.onnx"))
    has_json = any(base.glob("*.json"))

    if exe.exists() and has_model and has_json:
        print("[OK] ✅ Piper TTS erfolgreich installiert!")
        return 0
    else:
        print("[FEHLER] ❌ Piper Installation unvollstaendig!")
        print(f"  piper.exe: {exe.exists()}")
        print(f"  *.onnx: {has_model}")
        print(f"  *.json: {has_json}")
        print("  Fallback zu pyttsx3 wird verwendet.")
        return 1

if __name__ == "__main__":
    sys.exit(setup_piper())
