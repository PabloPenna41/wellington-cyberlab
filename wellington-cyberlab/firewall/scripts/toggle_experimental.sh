#!/usr/bin/env bash
# ==============================================================================
# Wellington CyberLab — Controle Seguro do Firewall Experimental
# Alterna entre Ativar, Desativar ou Limpar as regras experimentais
# sem afetar as regras essenciais do sistema.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RULES_DIR="$(cd "$SCRIPT_DIR/../rules" && pwd)"
PERM_FILE="$RULES_DIR/permanent_rules.nft"
EXP_FILE="$RULES_DIR/experimental_rules.nft"

ACTION="${1:-status}"

check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "[-] Erro: Este script requer privilégios de root para manipular o nftables."
        echo "    Execute: sudo bash $0 $ACTION"
        exit 1
    fi
}

case "$ACTION" in
    disable-all-firewall)
        check_root
        echo "[!] DESATIVANDO O FIREWALL COMPLETAMENTE (MODO ABERTO)..."
        # Remove a tabela experimental se existir
        if nft list tables | grep -q "table inet wellington_experimental"; then
            nft delete table inet wellington_experimental || true
        fi
        # Remove a tabela permanente do laboratório
        if nft list tables | grep -q "table inet wellington_permanent"; then
            nft delete table inet wellington_permanent || true
        fi
        # Desativa temporariamente o UFW caso esteja ativo
        if command -v ufw >/dev/null 2>&1; then
            ufw disable || true
        fi
        echo "[⚠️] FIREWALL COMPLETAMENTE DESATIVADO! Todas as portas estão abertas e sem filtragem."
        ;;

    enable-all-firewall)
        check_root
        echo "[+] ATIVANDO E RESTAURANDO O FIREWALL COMPLETO..."
        nft -f "$PERM_FILE"
        if command -v ufw >/dev/null 2>&1; then
            ufw --force enable || true
        fi
        echo "[✓] FIREWALL BLINDADO E ATIVO COM SUCESSO!"
        ;;

    load-permanent)
        check_root
        echo "[+] Aplicando regras PERMANENTES do CyberLab..."
        nft -f "$PERM_FILE"
        echo "[✓] Regras permanentes ativas com sucesso (table inet wellington_permanent)."
        ;;

    enable-experimental)
        check_root
        echo "[+] Carregando regras EXPERIMENTAIS do laboratório..."
        nft -f "$EXP_FILE"
        echo "[✓] Regras experimentais ativas (table inet wellington_experimental)."
        ;;

    disable-experimental)
        check_root
        echo "[!] Desativando exclusivamente as regras EXPERIMENTAIS..."
        if nft list tables | grep -q "table inet wellington_experimental"; then
            nft delete table inet wellington_experimental
            echo "[✓] Tabela experimental removida com êxito! As regras permanentes continuam ativas."
        else
            echo "[i] Nenhuma tabela experimental estava ativa."
        fi
        ;;

    block-ip)
        check_root
        BLOCK_IP="${2:-}"
        if [ -z "$BLOCK_IP" ]; then
            echo "[-] Informe o IP para quarentena. Exemplo: $0 block-ip 192.168.1.100"
            exit 1
        fi
        # Garantir que a tabela experimental existe
        if ! nft list tables | grep -q "table inet wellington_experimental"; then
            nft -f "$EXP_FILE"
        fi
        nft add element inet wellington_experimental redteam_blacklist { "$BLOCK_IP" }
        echo "[✓] IP $BLOCK_IP adicionado a lista de quarentena experimental!"
        ;;

    unblock-ip)
        check_root
        UNBLOCK_IP="${2:-}"
        if [ -z "$UNBLOCK_IP" ]; then
            echo "[-] Informe o IP para liberar."
            exit 1
        fi
        nft delete element inet wellington_experimental redteam_blacklist { "$UNBLOCK_IP" } || true
        echo "[✓] IP $UNBLOCK_IP removido da quarentena!"
        ;;

    status)
        echo "=========================================================="
        echo "   STATUS DAS TABELAS DO NFTABLES (WELLINGTON CYBERLAB)"
        echo "=========================================================="
        if nft list tables | grep -q "wellington_permanent"; then
            echo "[✓] REGRAS PERMANENTES: ATIVAS"
        else
            echo "[!] REGRAS PERMANENTES: NÃO CARREGADAS"
        fi

        if nft list tables | grep -q "wellington_experimental"; then
            echo "[⚠️] REGRAS EXPERIMENTAIS: ATIVAS (Laboratório em Modo Teste)"
        else
            echo "[i] REGRAS EXPERIMENTAIS: INATIVAS (Proteção Limpa Padrão)"
        fi
        echo "----------------------------------------------------------"
        ;;

    *)
        echo "Uso: $0 {enable-all-firewall|disable-all-firewall|load-permanent|enable-experimental|disable-experimental|block-ip <ip>|unblock-ip <ip>|status}"
        exit 1
        ;;

esac
