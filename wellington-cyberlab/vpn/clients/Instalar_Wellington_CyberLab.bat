@echo off
:: ==============================================================================
:: Wellington CyberLab — Instalador Oficial para Windows
:: Duplo-clique para iniciar: Eleva privilégios via UAC e abre a interface gráfica.
:: ==============================================================================
setlocal EnableDelayedExpansion
title Wellington CyberLab Setup

:: 1. Verificar privilégios de Administrador e solicitar elevação se necessário
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] Solicitando elevacao de privilegios administrativos...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

:: 2. Verificar se o Python está presente no PATH
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] Python nao detectado. Baixando e instalando Python oficial silenciosamente...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$url = 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe';" ^
        "$out = '$env:TEMP\python_setup.exe';" ^
        "Write-Host 'Baixando Python oficial...';" ^
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
        "(New-Object System.Net.WebClient).DownloadFile($url, $out);" ^
        "Write-Host 'Instalando...';" ^
        "Start-Process -FilePath $out -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait;"
)

:: 3. Executar o assistente gráfico de instalação
if exist "installer_gui.pyw" (
    start "" pythonw.exe "installer_gui.pyw"
) else (
    start "" python.exe "installer_gui.pyw"
)

exit /b
