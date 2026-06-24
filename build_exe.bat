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
if not defined LOCAL_BUILD set "LOCAL_BUILD=C:\_Local_DEV\codex_build\23tovcf_pro"
set "LOCAL_WORK=%LOCAL_BUILD%\build"
set "LOCAL_DIST=%LOCAL_BUILD%\dist"
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller ist nicht installiert.
    echo Bitte ausfuehren: python -m pip install pyinstaller
    pause
    exit /b 1
)
powershell -NoProfile -Command "Remove-Item -LiteralPath '%LOCAL_BUILD%' -Recurse -Force -ErrorAction SilentlyContinue; New-Item -ItemType Directory -Force -Path '%LOCAL_WORK%','%LOCAL_DIST%','dist' | Out-Null"
python -m PyInstaller --noconfirm --clean --workpath "%LOCAL_WORK%" --distpath "%LOCAL_DIST%" 23toVCF_Pro.spec
if errorlevel 1 (
    pause
    exit /b 1
)
if exist "%LOCAL_DIST%\23toVCF_Pro.exe" copy /Y "%LOCAL_DIST%\23toVCF_Pro.exe" "dist\23toVCF_Pro.exe" >nul
if exist "dist\23toVCF_Pro.exe" copy /Y "dist\23toVCF_Pro.exe" "23toVCF_Pro.exe" >nul
echo Fertig: dist\23toVCF_Pro.exe
