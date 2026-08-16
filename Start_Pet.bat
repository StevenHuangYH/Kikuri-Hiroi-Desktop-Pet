@echo off
title Kikuri Hiroi Desktop Pet
cd /d "%~dp0"
where pythonw >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    start "" pythonw "%~dp0desktop_pet.py"
) else (
    start "" python "%~dp0desktop_pet.py"
)
exit
