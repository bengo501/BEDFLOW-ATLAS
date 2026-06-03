@echo off
rem cria/atualiza o atalho do bed wizard na area de trabalho (clique duplo)
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_atalho_desktop.ps1"
echo.
pause
