@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    pause
    exit /b 1
)
echo Starte Genotype-to-VCF Pro...
python "Make23toVCF3.py"
if errorlevel 1 pause
