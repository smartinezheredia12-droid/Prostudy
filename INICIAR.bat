@echo off
title ProStudy - Servidor Local
color 0A
echo.
echo  =====================================================
echo   PROSTUDY - Fight Procrastination
echo   Iniciando servidor local...
echo  =====================================================
echo.

REM Verificar que el entorno virtual existe
if not exist venv (
    echo  [ERROR] No se encontro el entorno virtual.
    echo  Por favor ejecuta primero INSTALAR.bat
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar que Django esta instalado
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Django no esta instalado.
    echo  Por favor ejecuta primero INSTALAR.bat
    echo.
    pause
    exit /b 1
)

REM Aplicar migraciones nuevas si las hay
python manage.py migrate --run-syncdb >nul 2>&1

echo  [OK] Servidor listo en: http://127.0.0.1:8000
echo.
echo  USUARIO ADMIN: ADMIN  /  CONTRASENA: AdMiN2026
echo.
echo  Para detener el servidor presiona CTRL+C
echo  =====================================================
echo.

REM Abrir el navegador despues de 2 segundos
start /b cmd /c "timeout /t 2 >nul && start http://127.0.0.1:8000"

REM Iniciar el servidor Django
python manage.py runserver 127.0.0.1:8000
echo.
echo  Servidor detenido. Cierra esta ventana o ejecuta
echo  INICIAR.bat nuevamente para volver a arrancar.
echo.
pause
