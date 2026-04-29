@echo off
title ProStudy - Instalacion
color 0E
echo.
echo  =====================================================
echo   PROSTUDY - Fight Procrastination
echo   Instalacion del entorno local
echo  =====================================================
echo.

REM Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no esta instalado o no esta en el PATH.
    echo.
    echo  Por favor instala Python desde: https://www.python.org/downloads/
    echo  IMPORTANTE: Al instalar, marca la casilla "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo  [OK] Python encontrado:
python --version
echo.

REM Crear entorno virtual
echo  Creando entorno virtual...
if exist venv (
    echo  Borrando entorno virtual anterior para instalacion limpia...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo  [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)
echo  [OK] Entorno virtual creado.
echo.

REM Activar entorno virtual
echo  Activando entorno virtual...
call venv\Scripts\activate.bat
echo  [OK] Entorno virtual activado.
echo.

REM Instalar dependencias
echo  Instalando dependencias (puede tardar unos minutos)...
pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  [ERROR] Fallo la instalacion de dependencias. Revisa el error de arriba.
    pause
    exit /b 1
)
echo  [OK] Dependencias instaladas.
echo.

REM Aplicar migraciones
echo  Configurando base de datos...
python manage.py migrate --run-syncdb
if errorlevel 1 (
    echo  [ERROR] Fallo la configuracion de la base de datos.
    pause
    exit /b 1
)
echo  [OK] Base de datos configurada.
echo.

REM Crear datos iniciales (admin + frases)
echo  Creando usuario administrador y frases motivacionales...
python manage.py setup_initial_data
echo.

REM Recolectar archivos estaticos
echo  Configurando archivos estaticos...
python manage.py collectstatic --no-input --clear >nul 2>&1
echo  [OK] Archivos estaticos listos.
echo.

echo  =====================================================
echo   INSTALACION COMPLETADA CON EXITO
echo  =====================================================
echo.
echo   Usuario administrador creado:
echo     Usuario:    ADMIN
echo     Contrasena: AdMiN2026
echo.
echo   Ahora puedes ejecutar INICIAR.bat para arrancar
echo   la aplicacion en tu navegador.
echo.
pause
