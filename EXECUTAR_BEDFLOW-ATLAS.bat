@echo off
rem ============================================================
rem  BEDFLOW-ATLAS  -  EXECUTAVEL PRINCIPAL (clique duplo)
rem  este e o ponto de entrada do projeto: abre o wizard de
rem  leitos (.bed) no terminal e executa: python bed_wizard.py
rem
rem  encaminha para o launcher bed_wizard_terminal.bat na raiz.
rem ============================================================
cd /d "%~dp0"
call "%~dp0bed_wizard_terminal.bat" %*
