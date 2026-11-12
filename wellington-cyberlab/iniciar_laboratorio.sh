#!/usr/bin/env bash
# ==============================================================================
# Wellington CyberLab — Script de Inicialização Rápida de Todas as Aplicações
# ==============================================================================
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAB_ROOT="$DIR"

echo "[+] Inicializando Ecossistema Wellington CyberLab..."

# 1. Garantir que o Backend FastAPI está rodando na porta 8000
if ! ss -tlpn | grep -q ":8000"; then
    echo "[*] Iniciando Backend Administrativo & API..."
    nohup python3 -m uvicorn main:app --app-dir "$LAB_ROOT/backend/api" --host 0.0.0.0 --port 8000 >/dev/null 2>&1 &
    sleep 1
fi

# 2. Iniciar Aplicação 1: Wellington ERP (A Empresa na LAN)
echo "[*] Abrindo Aplicação 1: Wellington ERP Enterprise (Estilo TOTVS)..."
nohup python3 "$LAB_ROOT/gui/wellington_erp_app.py" >/dev/null 2>&1 &

# 3. Iniciar Aplicação 2: Blue Team Control Center (Defesa & Firewall Nftables)
echo "[*] Abrindo Aplicação 2: Blue Team Control Center (SOC Host)..."
nohup python3 "$LAB_ROOT/gui/control_center.py" >/dev/null 2>&1 &

# 4. Iniciar Aplicação 3: Red Team Station (O Invasor de Fora)
echo "[*] Abrindo Aplicação 3: Red Team Station (Auditoria Ofensiva)..."
nohup python3 "$LAB_ROOT/gui/red_team_station.py" >/dev/null 2>&1 &


echo "[✓] Todas as 3 aplicações foram abertas com sucesso!"
