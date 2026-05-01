@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    pause
    exit /b 1
)
echo Baue 23toVCF_Pro.exe...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller ist nicht installiert.
    echo Bitte ausfuehren: python -m pip install pyinstaller
    pause
    exit /b 1
)
powershell -NoProfile -Command "Get-ChildItem -LiteralPath 'build','dist' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force"
python -m PyInstaller --noconfirm 23toVCF_Pro.spec
if errorlevel 1 (
    pause
    exit /b 1
)
if exist "dist\23toVCF_Pro.exe" copy /Y "dist\23toVCF_Pro.exe" "23toVCF_Pro.exe" >nul
echo Fertig: dist\23toVCF_Pro.exe
