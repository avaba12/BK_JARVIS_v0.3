@echo off
title J.A.R.V.I.S v3.0 - Automatische Installation
color 0a
cd /d "%~dp0"

echo.
echo ============================================
echo   J.A.R.V.I.S v3.0 - Automatische Installation
echo ============================================
echo.

:: Pruefe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo Bitte installiere Python 3.10+ von https://python.org
    echo WICHTIG: Bei Installation "Add Python to PATH" aktivieren!
    pause
    exit /b 1
)
python --version
echo.

:: Pruefe pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] pip ist nicht verfuegbar!
    pause
    exit /b 1
)

:: Erstelle venv
if not exist "venv" (
    echo [1/8] Erstelle virtuelle Umgebung...
    python -m venv "venv"
    if errorlevel 1 (
        echo [FEHLER] venv konnte nicht erstellt werden!
        pause
        exit /b 1
    )
    echo [OK] venv erstellt
) else (
    echo [OK] venv existiert bereits
)
echo.

:: Aktiviere venv
echo [2/8] Aktiviere virtuelle Umgebung...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [FEHLER] venv konnte nicht aktiviert werden!
    pause
    exit /b 1
)
echo [OK] venv aktiviert
echo.

:: Upgrade pip
echo [3/8] Upgrade pip...
python -m pip install --upgrade pip setuptools wheel
echo.

:: Installiere ALLE Python-Pakete
echo [4/8] Installiere Python-Pakete... (das kann einige Minuten dauern)
echo.
pip install PyQt6 requests psutil ollama pyttsx3 soundfile sounddevice pyaudio SpeechRecognition vosk pyautogui pyperclip mss Pillow opencv-python numpy python-dotenv pydantic send2trash PyPDF2 pdfplumber python-docx beautifulsoup4 edge-tts duckduckgo-search playwright google-generativeai google-genai
echo.
echo [OK] Python-Pakete installiert
echo.

:: Installiere Playwright Browser
echo [5/8] Installiere Playwright Browser...
python -m playwright install chromium
echo.

:: Lade Piper TTS
echo [6/8] Lade Piper TTS (~70MB)...
python "setup_piper.py"
echo.

:: Lade Vosk STT
echo [7/8] Lade Vosk STT (~50MB)...
python "setup_vosk.py"
echo.

:: Erstelle Ordnerstruktur
echo [8/8] Erstelle Ordnerstruktur...
if not exist "config" mkdir "config"
if not exist "data" mkdir "data"
if not exist "logs" mkdir "logs"
if not exist "plugins" mkdir "plugins"
if not exist "workflows\bilder" mkdir "workflows\bilder"
if not exist "workflows\videos" mkdir "workflows\videos"
if not exist "workflows\musik" mkdir "workflows\musik"
if not exist "outputs\comfyui" mkdir "outputs\comfyui"
echo [OK] Ordner erstellt
echo.

:: Erstelle Default-Config
echo [INFO] Erstelle Konfiguration...
if not exist "config\settings.json" (
    python -c "import json; open('config/settings.json','w').write(json.dumps({'user_name':'Sir','language':'de-DE','theme':'dark','tts_engine':'piper','tts_voice':'thorsten-de-medium','tts_speed':1.0,'tts_volume':0.9,'stt_engine':'vosk','wake_word':'jarvis','sleep_word':'danke schlaf','ollama_host':'http://localhost:11434','chat_model':'llama3','code_model':'codellama','vision_model':'llava','temperature':0.7,'top_p':0.9,'memory_limit':1000,'auto_cleanup':True,'pin_enabled':False,'pin_code':'','session_timeout':30,'confirmation_required':True,'offline_mode':True,'use_local_wake_word':True,'show_thinking':False,'thinking_mode':'instant','allowed_apps':['notepad','chrome','vscode','explorer','cmd','spotify','discord'],'allowed_urls':[],'skills':{'web_search':True,'file_access':True,'comfyui':False,'pc_control':True,'plugins':True,'telegram':False,'discord':False,'home_assistant':False,'obsidian':False,'voice_control':True,'rag':True},'master_mode':'standard','comfyui_url':'http://127.0.0.1:8188','comfyui_output_dir':'outputs/comfyui','rocm_path':'C:/Program Files/AMD/ROCm/6.1/bin','piper_model':'thorsten-de-medium','piper_path':'models/piper','vosk_model':'vosk-model-small-de-0.15'},indent=4))"
    echo [OK] settings.json erstellt
) else (
    echo [OK] settings.json existiert bereits
)

if not exist "config\api_keys.json" (
    python -c "import json; open('config/api_keys.json','w').write(json.dumps({'gemini_api_key':'','telegram_bot_token':'','discord_webhook':'','home_assistant_url':'','home_assistant_token':'','smtp_server':'','smtp_port':587,'smtp_user':'','smtp_password':'','email_from':''},indent=4))"
    echo [OK] api_keys.json erstellt
) else (
    echo [OK] api_keys.json existiert bereits
)
echo.

:: Pruefe Ollama
echo [INFO] Pruefe Ollama...
python -c "import urllib.request; urllib.request.urlopen('http://localhost:11434', timeout=3)" >nul 2>&1
if errorlevel 1 (
    echo [WARNUNG] Ollama laeuft nicht!
    echo.
    echo    Bitte installiere Ollama: https://ollama.com
    echo    Danach starte es mit: ollama serve
    echo    oder ollama run llama3
    echo.
) else (
    echo [OK] Ollama laeuft bereits
)
echo.

:: === AMD GPU / ROCm AUTO-ERKENNUNG ===
echo [INFO] Pruefe AMD GPU...
python -c "
import subprocess, sys
try:
    result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], capture_output=True, text=True)
    output = result.stdout.lower()
    if 'amd' in output or 'radeon' in output or 'rx ' in output:
        print('AMD_GPU_FOUND')
        sys.exit(0)
except:
    pass
sys.exit(1)
" >nul 2>&1

if %errorlevel% == 0 (
    echo [INFO] AMD GPU erkannt!

    :: Pruefe ob ROCm schon installiert ist
    if exist "C:\Program Files\AMD\ROCm\6.1\bin\rocm-smi.exe" (
        echo [OK] AMD ROCm ist bereits installiert
    ) else (
        echo.
        echo [INFO] AMD ROCm fuer GPU-Monitoring wird benoetigt.
        echo [INFO] ROCm ist ein GPU-Computing-Framework (ca. 2-3 GB).
        echo.
        echo    Moeglichkeiten:
        echo    1. J.A.R.V.I.S laedt den Installer herunter und startet ihn
        echo    2. Du ueberspringst ROCm (GPU-Monitoring funktioniert dann eingeschraenkt)
        echo.

        set /p rocm_choice="ROCm Installer herunterladen? (j/n): "

        if /i "%rocm_choice%"=="j" (
            echo.
            echo [INFO] Lade AMD HIP SDK Installer herunter...
            echo    Das kann einige Minuten dauern (ca. 2-3 GB)...
            echo.

            :: Lade Installer herunter (AMD HIP SDK 6.1.2)
            powershell -Command "& {Invoke-WebRequest -Uri 'https://download.amd.com/developer/eula/rocm/6.1.2/AMD-Software-PRO-Edition-23.Q4-Win10-Win11-For-HIP.exe' -OutFile 'rocm_installer.exe'}" 2>nul

            if exist "rocm_installer.exe" (
                echo [OK] Installer heruntergeladen: rocm_installer.exe
                echo.
                echo [INFO] Starte AMD Installer...
                echo    WICHTIG: Der Installer braucht Administrator-Rechte!
                echo    Bitte klicke im UAC-Fenster auf 'Ja'.
                echo    Danach einfach 'Next -> Next -> Install' klicken.
                echo.
                start /wait rocm_installer.exe
                echo.
                echo [INFO] Nach der ROCm-Installation bitte PC neu starten!
                echo    Dann J.A.R.V.I.S neu starten.
            ) else (
                echo [FEHLER] Download fehlgeschlagen.
                echo    Bitte manuell herunterladen:
                echo    https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html
            )
        ) else (
            echo [INFO] ROCm wird uebersprungen.
            echo    GPU-Monitoring zeigt dann nur grundlegende Infos.
        )
    )
) else (
    echo [INFO] Keine AMD GPU erkannt - pruefe NVIDIA...
    python -c "
import subprocess, sys
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    if result.returncode == 0:
        print('NVIDIA_GPU_FOUND')
        sys.exit(0)
except:
    pass
sys.exit(1)
" >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] NVIDIA GPU erkannt - nvidia-smi verfuegbar
    ) else (
        echo [INFO] Keine dedizierte GPU erkannt oder Treiber nicht installiert.
        echo    GPU-Monitoring wird eingeschraenkt funktionieren.
    )
)
echo.

:: Fertig
echo ============================================
echo   INSTALLATION ABGESCHLOSSEN!
echo ============================================
echo.
echo [OK] Alles ist installiert und bereit!
echo.
echo    Starte J.A.R.V.I.S jetzt mit: start.bat
echo.
echo    WICHTIGE HINWEISE:
echo    - Ollama muss laufen fuer die KI-Funktionen
echo    - ComfyUI muss separat installiert werden fuer Bildgenerierung
echo    - Fuer Online-Features: API-Keys in Einstellungen eintragen
echo.
if exist "rocm_installer.exe" (
    echo    - ROCm Installer liegt hier: rocm_installer.exe
echo      Loesche ihn nach erfolgreicher Installation.
echo.
)
pause
