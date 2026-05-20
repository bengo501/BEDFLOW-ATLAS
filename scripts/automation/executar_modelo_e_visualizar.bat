@echo off
setlocal

rem raiz do repositorio
cd /d "%~dp0..\.."

echo gerando malha do cilindro e particulas...
python "tools\vis_cilindro\modelo_cilindro.py"
if errorlevel 1 (
    echo houve um erro ao gerar a malha ou as particulas.
    echo verifique as mensagens acima.
    echo.
    pause
    goto :fim
)

echo.
echo abrindo visualizacao em opengl...
python "tools\vis_cilindro\visualizador.py"

:fim
echo.
echo execucao finalizada.
pause

