@echo off
title Wellington CyberLab Launcher
cd /d "%~dp0"

:: 1. Procurar pythonw no PATH
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    if exist "wellington_client_win.pyw" (
        start "" pythonw "wellington_client_win.pyw"
        exit /b
    )
    if exist "bin\wellington_client_win.pyw" (
        start "" pythonw "bin\wellington_client_win.pyw"
        exit /b
    )
    if exist "C:\WellingtonCyberLab\bin\wellington_client_win.pyw" (
        start "" pythonw "C:\WellingtonCyberLab\bin\wellington_client_win.pyw"
        exit /b
    )
)

:: 2. Fallback caso pythonw nao esteja no PATH, procurar no AppData
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\pythonw.exe" (
        if exist "C:\WellingtonCyberLab\bin\wellington_client_win.pyw" (
            start "" "%%D\pythonw.exe" "C:\WellingtonCyberLab\bin\wellington_client_win.pyw"
            exit /b
        )
    )
)

:: 3. Se ainda assim nao achar, usar python normal
start "" python "wellington_client_win.pyw"
exit /b
