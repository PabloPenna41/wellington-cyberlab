#!/usr/bin/env bash
# ==============================================================================
# Wellington CyberLab — Script para Fechar Todas as Aplicações com 1 Comando
# ==============================================================================
echo "[!] Encerrando todas as aplicações do Wellington CyberLab..."

pkill -9 -f "wellington_erp_app.py" 2>/dev/null || true
pkill -9 -f "control_center.py" 2>/dev/null || true
pkill -9 -f "red_team_station.py" 2>/dev/null || true

echo "[✓] Todas as janelas do laboratório foram fechadas com sucesso!"
