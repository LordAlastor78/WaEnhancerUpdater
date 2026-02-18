@echo off
REM WaEnhancer Compatibility Checker - Launcher
REM Ejecuta el checker de compatibilidad

echo.
echo ===================================
echo  WaEnhancer Compatibility Checker
echo ===================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
pip show requests >nul 2>&1
if errorlevel 1 (
    echo [!] Instalando dependencias...
    pip install -r requirements.txt
    echo.
)

REM Ejecutar el script
python waenhancer_checker.py

echo.
pause
