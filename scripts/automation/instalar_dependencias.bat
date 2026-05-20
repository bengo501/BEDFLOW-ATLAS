@echo off
setlocal

rem raiz do repositorio
cd /d "%~dp0..\.."

echo atualizando pip...
python -m pip install --upgrade pip

echo instalando dependencias de visualizacao a partir de requirements-visualizacao.txt...
python -m pip install -r "requirements-visualizacao.txt"

echo.
echo instalacao de dependencias concluida.
echo.
pause

