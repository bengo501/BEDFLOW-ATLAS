@echo off
rem ============================================================
rem  BEDFLOW-ATLAS  -  launcher do wizard de leitos (.bed)
rem  abre um terminal e executa: python bed_wizard.py
rem  (este .bat fica na raiz do repositorio; %~dp0 = raiz)
rem ============================================================
chcp 65001 >nul
setlocal
title BEDFLOW-ATLAS - bed wizard (terminal)

rem -- usar a pasta deste script como diretorio de trabalho (raiz do repo) --
cd /d "%~dp0"

echo ============================================================
echo   BEDFLOW-ATLAS  -  wizard de leitos empacotados (.bed)
echo ============================================================
echo.
echo  pasta: %cd%
echo.

rem -- localizar interpretador python (py launcher tem prioridade) --
set "PY_CMD="
where py >nul 2>&1 && set "PY_CMD=py"
if not defined PY_CMD (
    where python >nul 2>&1 && set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [erro] python nao encontrado no PATH.
    echo        instale python 3.8+ em https://python.org
    echo        e marque a opcao "Add python.exe to PATH" no instalador.
    echo.
    pause
    exit /b 1
)

rem -- verificar a interface rica do terminal (rich / prompt_toolkit) --
%PY_CMD% -c "import rich, prompt_toolkit" >nul 2>&1
if not errorlevel 1 goto :run

echo [aviso] dependencias da interface do terminal nao encontradas.
set /p "_INSTALL=instalar agora com pip? [S/n] "
if /i "%_INSTALL%"=="n" goto :run
echo.
echo instalando dsl\requirements-terminal.txt ...
%PY_CMD% -m pip install -r "dsl\requirements-terminal.txt"
echo.

:run
echo iniciando o wizard... (use o menu; escolha "sair" para fechar)
echo.
%PY_CMD% bed_wizard.py
set "_RC=%errorlevel%"

echo.
if not "%_RC%"=="0" (
    echo [o wizard terminou com codigo %_RC%]
    pause
)
endlocal
