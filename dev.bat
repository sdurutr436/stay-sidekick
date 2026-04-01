@echo off
REM =============================================================================
REM Stay Sidekick — Script de desarrollo (Windows)
REM Levanta 11ty y Angular en paralelo
REM
REM Uso: Doble clic o ejecutar desde cmd / PowerShell
REM =============================================================================

echo.
echo  Stay Sidekick - Entorno de desarrollo
echo  ----------------------------------------
echo  Sitio estatico (11ty)  -^>  http://localhost:8080
echo  App Angular            -^>  http://localhost:4200
echo  ----------------------------------------
echo.

REM Instala dependencias raiz si no existen
if not exist "node_modules\" (
    echo Instalando dependencias raiz...
    call npm install
)

REM Instala dependencias de frontend si no existen
if not exist "frontend\node_modules\" (
    echo Instalando dependencias de frontend...
    call npm --prefix frontend install
)

REM Instala dependencias de web si no existen
if not exist "web\node_modules\" (
    echo Instalando dependencias de web...
    call npm --prefix web install
)

echo Levantando servidores...
call npm run dev
