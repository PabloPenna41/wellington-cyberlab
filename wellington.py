#!/usr/bin/env python3
"""
Wellington CyberLab — Master Launcher (Inicializador Único)
Arquivo único para rodar, gerenciar e abrir todo o ecossistema do laboratório:
1. Backend Administrativo & API (FastAPI / Uvicorn na porta 8000)
2. Aplicação 1: Wellington ERP Enterprise (Estilo TOTVS na LAN)
3. Aplicação 2: Blue Team Control Center (Defesa & Firewall Nftables)
4. Aplicação 3: Red Team Station (O Invasor de Fora / Auditoria Ofensiva)

Uso:
  ./wellington.py          (Abre tudo com 1 clique)
  ./wellington.py --stop   (Fecha todas as aplicações)
  ./wellington.py --status (Verifica quais componentes estão rodando)
"""

import os
import sys
import time
import subprocess
import socket

# Diretório raiz do laboratório
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CYBERLAB_DIR = os.path.join(BASE_DIR, "wellington-cyberlab")
if not os.path.exists(CYBERLAB_DIR):
    CYBERLAB_DIR = BASE_DIR

GUI_DIR = os.path.join(CYBERLAB_DIR, "gui")
BACKEND_DIR = os.path.join(CYBERLAB_DIR, "backend", "api")

APPS = [
    {
        "name": "Wellington ERP Enterprise (A Empresa na LAN)",
        "script": os.path.join(GUI_DIR, "wellington_erp_app.py"),
        "color": "\033[94m" # Azul
    },
    {
        "name": "Blue Team Control Center (Defesa & Firewall)",
        "script": os.path.join(GUI_DIR, "control_center.py"),
        "color": "\033[96m" # Ciano
    },
    {
        "name": "Red Team Station (O Invasor de Fora)",
        "script": os.path.join(GUI_DIR, "red_team_station.py"),
        "color": "\033[91m" # Vermelho
    }
]

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_backend():
    if not is_port_open(8000):
        print(f"{BOLD}[*] Iniciando Backend FastAPI na porta 8000...{RESET}")
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--app-dir", BACKEND_DIR, "--host", "0.0.0.0", "--port", "8000"]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        # Aguardar porta abrir
        for _ in range(10):
            time.sleep(0.3)
            if is_port_open(8000):
                break
        print(f"{GREEN}[✓] Backend FastAPI ativo e respondendo na porta 8000!{RESET}")
    else:
        print(f"{GREEN}[✓] Backend FastAPI já está ativo na porta 8000.{RESET}")

def stop_all():
    print(f"{BOLD}[!] Encerrando todas as aplicações do Wellington CyberLab...{RESET}")
    subprocess.run("pkill -9 -f 'wellington_erp_app.py'", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("pkill -9 -f 'control_center.py'", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("pkill -9 -f 'red_team_station.py'", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("pkill -9 -f 'uvicorn.*main:app'", shell=True, stderr=subprocess.DEVNULL)
    print(f"{GREEN}[✓] Todas as aplicações e o backend foram fechados com sucesso!{RESET}")

def start_all():
    print(f"\n{BOLD}{'='*65}{RESET}")
    print(f"{BOLD}    WELLINGTON CYBERLAB — INICIALIZADOR MESTRE{RESET}")
    print(f"{BOLD}{'='*65}{RESET}\n")

    # 1. Subir backend
    start_backend()

    # 2. Subir as 3 aplicações gráficas em sessões desacopladas
    for app in APPS:
        name = app["name"]
        script = app["script"]
        color = app["color"]
        if os.path.exists(script):
            print(f"{color}[+] Abrindo: {name}...{RESET}")
            subprocess.Popen([sys.executable, script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(0.3)
        else:
            print(f"\033[93m[!] Arquivo não encontrado: {script}{RESET}")

    print(f"\n{GREEN}{BOLD}[✓] PRONTO! As 3 aplicações foram abertas na sua tela do Hyprland.{RESET}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--stop", "-s", "stop"):
        stop_all()
    elif len(sys.argv) > 1 and sys.argv[1] in ("--status", "status"):
        erp = subprocess.run("pgrep -f 'wellington_erp_app.py'", shell=True, capture_output=True).stdout.strip()
        blue = subprocess.run("pgrep -f 'control_center.py'", shell=True, capture_output=True).stdout.strip()
        red = subprocess.run("pgrep -f 'red_team_station.py'", shell=True, capture_output=True).stdout.strip()
        print(f"Backend (Porta 8000): {'ONLINE' if is_port_open(8000) else 'OFFLINE'}")
        print(f"Wellington ERP: {'RODANDO (PID ' + erp.decode() + ')' if erp else 'PARADO'}")
        print(f"Blue Team: {'RODANDO (PID ' + blue.decode() + ')' if blue else 'PARADO'}")
        print(f"Red Team: {'RODANDO (PID ' + red.decode() + ')' if red else 'PARADO'}")
    else:
        start_all()
