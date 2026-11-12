#!/usr/bin/env python3
"""
Wellington CyberLab — Backend Administrativo, ERP e Motor de Estado do Firewall
Fornece telemetria, simulação integrada de regras Nftables, proteção de endpoints e banco de dados corporativo.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import shutil
import socket
import os
import psutil
import time
import sqlite3
from datetime import datetime
from typing import Dict, Any, List

app = FastAPI(
    title="Wellington CyberLab API & Host",
    version="2.0.0",
    description="API de telemetria, controle de Firewall Nftables e Wellington ERP"
)

# Caminho dinâmico para o site estático público e banco ERP
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "website", "public")
DB_ERP = os.path.join(BASE_DIR, "backend", "database", "wellington_erp.db")

# ==============================================================================
# ESTADO GLOBAL DO FIREWALL E TELEMETRIA DE PACOTES
# ==============================================================================
FIREWALL_ENABLED = True          # Estado Mestre do Firewall (Ativo vs Modo Aberto)
EXPERIMENTAL_ENABLED = True      # Regras de filtragem avançada (Rate-limit, Anti-BruteForce, Anti-SQLi)
QUARANTINE_ACTIVE = False        # Bloqueio total do IP do Red Team inclusive no site público

COUNTERS = {
    "accepted_packets": 42,
    "blocked_quarantine": 0,
    "blocked_ratelimit": 0,
    "blocked_sqli_waf": 0,
    "blocked_bruteforce": 0,
    "total_dropped": 0
}

SECURITY_EVENTS: List[str] = []
LAST_CRACKED_CREDENTIALS: Dict[str, Any] = {}


def log_security_event(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    SECURITY_EVENTS.append(entry)
    if len(SECURITY_EVENTS) > 200:
        SECURITY_EVENTS.pop(0)


log_security_event("[SISTEMA] Motor do Firewall Nftables inicializado em modo PROTEGIDO.")


def get_local_lan_ip() -> str:
    """Detecta dinamicamente o IP real da interface de rede ativa."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


# CORS liberado para os painéis locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = ["nginx", "ufw", "nftables", "suricata", "wg-quick@wg0"]


# ==============================================================================
# ENDPOINTS DE CONTROLE E INSPEÇÃO DO FIREWALL (BLUE TEAM <-> RED TEAM)
# ==============================================================================
@app.get("/api/firewall/state")
def get_firewall_state():
    if not FIREWALL_ENABLED:
        mode = "DESATIVADO / MODO ABERTO (VULNERÁVEL)"
    elif QUARANTINE_ACTIVE:
        mode = "QUARENTENA ATIVA (RED TEAM BLOQUEADO)"
    elif EXPERIMENTAL_ENABLED:
        mode = "ATIVO / BLINDADO (PERMANENTE + EXPERIMENTAL)"
    else:
        mode = "ATIVO / BÁSICO (SOMENTE REGRAS PERMANENTES)"

    return {
        "firewall_enabled": FIREWALL_ENABLED,
        "experimental_enabled": EXPERIMENTAL_ENABLED,
        "quarantine_active": QUARANTINE_ACTIVE,
        "mode": mode,
        "lan_ip": get_local_lan_ip(),
        "counters": COUNTERS,
        "recent_events": SECURITY_EVENTS[-30:]
    }


@app.get("/api/firewall/toggle-all")
def toggle_all_firewall(enable: bool = True):
    """Ativa ou Desativa o Firewall completamente."""
    global FIREWALL_ENABLED, EXPERIMENTAL_ENABLED, QUARANTINE_ACTIVE, LAST_CRACKED_CREDENTIALS
    FIREWALL_ENABLED = enable
    if not enable:
        EXPERIMENTAL_ENABLED = False
        QUARANTINE_ACTIVE = False
        log_security_event("[⚠️ ALERTA SOC] FIREWALL COMPLETAMENTE DESATIVADO! Servidor em Modo Aberto / Vulnerável.")
    else:
        EXPERIMENTAL_ENABLED = True
        QUARANTINE_ACTIVE = False
        LAST_CRACKED_CREDENTIALS = {}
        log_security_event("[🛡️ DEFESA SOC] FIREWALL ATIVADO E RESTAURADO (Modo Blindado). Regras carregadas.")

    return {
        "firewall_enabled": FIREWALL_ENABLED,
        "experimental_enabled": EXPERIMENTAL_ENABLED,
        "quarantine_active": QUARANTINE_ACTIVE,
        "msg": "Firewall ativado com proteção total" if enable else "Firewall TOTALMENTE DESATIVADO (Modo Aberto)"
    }


@app.get("/api/firewall/experimental/toggle")
def toggle_experimental_rules(enable: bool = True):
    """Ativa ou desativa as regras experimentais de contenção sem desligar as permanentes."""
    global FIREWALL_ENABLED, EXPERIMENTAL_ENABLED, QUARANTINE_ACTIVE
    if enable:
        FIREWALL_ENABLED = True
        EXPERIMENTAL_ENABLED = True
        log_security_event("[⚡ NFTABLES] Tabela 'wellington_experimental' ATIVADA (Anti-DoS, Anti-BruteForce e Anti-SQLi).")
    else:
        EXPERIMENTAL_ENABLED = False
        QUARANTINE_ACTIVE = False
        log_security_event("[🧹 NFTABLES] Tabela 'wellington_experimental' REMOVIDA. Apenas regras permanentes ativas.")

    return {
        "firewall_enabled": FIREWALL_ENABLED,
        "experimental_enabled": EXPERIMENTAL_ENABLED,
        "quarantine_active": QUARANTINE_ACTIVE
    }


@app.get("/api/firewall/quarantine/toggle")
def toggle_quarantine(enable: bool = True):
    """Permite ao Blue Team bloquear ou liberar o acesso do Red Team ao site e serviços."""
    global FIREWALL_ENABLED, EXPERIMENTAL_ENABLED, QUARANTINE_ACTIVE
    if enable:
        FIREWALL_ENABLED = True
        EXPERIMENTAL_ENABLED = True
        QUARANTINE_ACTIVE = True
        log_security_event("[🚫 QUARENTENA] IP do Red Team (10.77.0.2) bloqueado! Acesso ao site principal revogado (DROP).")
    else:
        QUARANTINE_ACTIVE = False
        log_security_event("[✅ QUARENTENA] IP do Red Team (10.77.0.2) liberado para acessar o site público.")

    return {
        "firewall_enabled": FIREWALL_ENABLED,
        "experimental_enabled": EXPERIMENTAL_ENABLED,
        "quarantine_active": QUARANTINE_ACTIVE,
        "msg": "Quarentena do Red Team atualizada"
    }


@app.get("/api/firewall/quarantine/status")
def get_quarantine_status():
    return {
        "quarantine_active": QUARANTINE_ACTIVE,
        "firewall_enabled": FIREWALL_ENABLED,
        "experimental_enabled": EXPERIMENTAL_ENABLED
    }


@app.get("/api/firewall/ruleset")
def get_firewall_ruleset():
    """Gera a visualização fiel das tabelas do Nftables com os contadores em tempo real."""
    lan_ip = get_local_lan_ip()
    acc = COUNTERS["accepted_packets"]
    acc_bytes = acc * 640
    drop_tot = COUNTERS["total_dropped"]
    drop_bytes = drop_tot * 128
    q_drop = COUNTERS["blocked_quarantine"]
    rl_drop = COUNTERS["blocked_ratelimit"]
    bf_drop = COUNTERS["blocked_bruteforce"] + COUNTERS["blocked_sqli_waf"]

    if not FIREWALL_ENABLED:
        ruleset_text = (
            "# ==============================================================================\n"
            "# ⚠️ ESTADO DO KERNEL NFTABLES: FIREWALL COMPLETAMENTE DESATIVADO (MODO ABERTO)\n"
            "# Nenhuma tabela de filtragem ativa (nft flush ruleset executado).\n"
            "# Todo o tráfego de entrada e tentativas de exploração estão passando livremente!\n"
            "# ==============================================================================\n"
        )
        return {"ruleset": ruleset_text, "events": SECURITY_EVENTS[-20:]}

    perm_table = f"""table inet wellington_permanent {{
    set admin_whitelist {{
        type ipv4_addr
        elements = {{ 127.0.0.1, {lan_ip} }}
    }}

    chain input {{
        type filter hook input priority filter; policy drop;
        iifname "lo" counter packets {acc} bytes {acc_bytes} accept comment "BlueTeam: Loopback essencial"
        ct state {{ established, related }} counter packets {acc * 2} bytes {acc_bytes * 3} accept comment "BlueTeam: Conntrack ativo"
        ct state invalid counter packets 0 bytes 0 drop comment "BlueTeam: Descartar pacotes invalidos"
        ip protocol icmp counter packets 12 bytes 1008 accept comment "BlueTeam: ICMP Diagnostico"
        tcp dport {{ 80, 443, 8000 }} counter packets {acc} bytes {acc_bytes} accept comment "BlueTeam: Portal Web Wellington"
        udp dport 51820 counter packets 8 bytes 1184 accept comment "BlueTeam: WireGuard VPN"
        tcp dport 22 counter packets 4 bytes 512 accept comment "BlueTeam: SSH Administrativo (Anti-Lockout)"
        limit rate 5/minute burst 10 packets log prefix "Wellington-FW-DROP: " flags all
        counter packets {drop_tot} bytes {drop_bytes} comment "BlueTeam: Pacotes Bloqueados pela Politica Padrao"
    }}
}}
"""

    exp_table = ""
    if EXPERIMENTAL_ENABLED:
        blacklist_elems = "{ 10.77.0.2, redteam_external }" if QUARANTINE_ACTIVE else "{ }"
        exp_table = f"""
table inet wellington_experimental {{
    set redteam_blacklist {{
        type ipv4_addr
        elements = {blacklist_elems}
    }}

    chain input_experimental {{
        type filter hook input priority filter - 5; policy accept;
        # Regra 1: Quarentena Dinâmica do Red Team (Bloqueio do Site e Serviços)
        ip saddr @redteam_blacklist log prefix "EXP-BLOCK-REDTEAM: " counter packets {q_drop} bytes {q_drop * 128} drop comment "Exp1: Quarentena Red Team"

        # Regra 2: Mitigação Anti-DoS / Flood HTTP (Máx 10 req/s)
        tcp dport {{ 80, 8000 }} ct state new meter http_flood {{ ip saddr limit rate over 10/second burst 15 packets }} counter packets {rl_drop} bytes {rl_drop * 128} drop comment "Exp2: Anti-Flood Rate Limit"

        # Regra 3: Proteção Ativa do ERP contra Força Bruta e SQL Injection
        tcp dport 8000 counter packets {bf_drop} bytes {bf_drop * 256} drop comment "Exp3: IPS / Protecao Login TOTVS & SQLi"

        # Regra 4: Rejeição Rápida com TCP Reset na porta 8080
        tcp dport 8080 counter packets 2 bytes 120 reject with tcp reset comment "Exp4: Rejeicao Rapida RST"
    }}
}}
"""

    return {"ruleset": perm_table + exp_table, "events": SECURITY_EVENTS[-20:]}


# ==============================================================================
# PORTAL INSTITUCIONAL PÚBLICO (WELLINGTON NEGÓCIOS)
# ==============================================================================
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def serve_home(client_mode: str = "normal"):
        global QUARANTINE_ACTIVE, FIREWALL_ENABLED
        # Se o Firewall estiver ativo, com quarentena ativa, e a requisição vier do Red Team:
        if FIREWALL_ENABLED and QUARANTINE_ACTIVE and client_mode == "redteam":
            COUNTERS["blocked_quarantine"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event("[🚫 NFTABLES DROP] Tentativa de acesso do Red Team ao Site Principal BARRADA pela Quarentena!")
            raise HTTPException(
                status_code=403,
                detail="[NFTABLES FIREWALL DROP] Conexão bloqueada pelo Blue Team! O acesso do Red Team ao site principal foi revogado."
            )

        COUNTERS["accepted_packets"] += 1
        if client_mode == "redteam":
            log_security_event("[🌐 NFTABLES ACCEPT] Red Team acessou o site público institucional (Porta 8000).")
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/style.css")
    def serve_css():
        return FileResponse(os.path.join(STATIC_DIR, "style.css"))


# ==============================================================================
# HEALTH CHECK & SIMULADOR DE RATE-LIMIT (FLOOD TEST)
# ==============================================================================
@app.get("/api/health")
def health_check(client_mode: str = "normal", flood_seq: int = 0) -> Dict[str, Any]:
    global FIREWALL_ENABLED, EXPERIMENTAL_ENABLED, QUARANTINE_ACTIVE

    if client_mode == "redteam":
        if FIREWALL_ENABLED and QUARANTINE_ACTIVE:
            COUNTERS["blocked_quarantine"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event(f"[🚫 NFTABLES DROP] Requisição #{flood_seq or 1} do Red Team descartada (IP em Quarentena).")
            raise HTTPException(
                status_code=403,
                detail="[NFTABLES DROP] IP do Red Team bloqueado em Quarentena!"
            )

        # Se for um teste de rajada (Flood) e o firewall/regras experimentais estiverem ativos:
        if flood_seq > 10 and FIREWALL_ENABLED and EXPERIMENTAL_ENABLED:
            COUNTERS["blocked_ratelimit"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event(f"[⚡ RATE-LIMIT DROP] Pacote Flood #{flood_seq} descartado (Acima de 10 req/s)!")
            raise HTTPException(
                status_code=429,
                detail="[NFTABLES RATE-LIMIT] Excesso de requisições bloqueado pela regra 'meter http_flood'!"
            )

    COUNTERS["accepted_packets"] += 1
    return {
        "status": "healthy",
        "lab": "Wellington CyberLab",
        "node": "CachyOS Server",
        "target": "Wellington Negócios ERP",
        "firewall_enabled": FIREWALL_ENABLED,
        "quarantine_active": QUARANTINE_ACTIVE
    }


# ==============================================================================
# ENDPOINTS DO ERP CORPORATIVO (WELLINGTON NEGÓCIOS - TOTVS)
# ==============================================================================
@app.get("/api/erp/clientes")
def get_erp_clientes() -> List[Dict[str, Any]]:
    """Retorna a lista de clientes VIP corporativos."""
    if not os.path.exists(DB_ERP):
        return []
    conn = sqlite3.connect(DB_ERP)
    cur = conn.cursor()
    cur.execute("SELECT id, razao_social, cnpj, contrato_mensal, status FROM clientes_vip")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "razao_social": r[1], "cnpj": r[2], "contrato": r[3], "status": r[4]} for r in rows]


@app.get("/api/erp/busca-vulneravel")
def search_vulnerable(q: str = "", client_mode: str = "redteam"):
    """Endpoint de demonstração de SQL Injection contra o ERP."""
    global FIREWALL_ENABLED, EXPERIMENTAL_ENABLED, QUARANTINE_ACTIVE

    if client_mode == "redteam":
        if FIREWALL_ENABLED and QUARANTINE_ACTIVE:
            COUNTERS["blocked_quarantine"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event("[🚫 NFTABLES DROP] Tentativa de SQLi bloqueada: IP do Red Team está em Quarentena!")
            raise HTTPException(
                status_code=403,
                detail="[NFTABLES FIREWALL DROP] Acesso negado: IP em Quarentena pelo Blue Team!"
            )
        if FIREWALL_ENABLED and EXPERIMENTAL_ENABLED:
            COUNTERS["blocked_sqli_waf"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event(f"[🛡️ FIREWALL/IPS DROP] Tentativa de SQL Injection ({q}) bloqueada pelo Firewall Ativo!")
            raise HTTPException(
                status_code=403,
                detail="[NFTABLES / IPS BLOCK] Ataque de SQL Injection interceptado pelo Firewall! (Desative o Firewall no Blue Team para demonstrar a vulnerabilidade)."
            )

    if not os.path.exists(DB_ERP):
        return {"error": "Banco não inicializado"}
    conn = sqlite3.connect(DB_ERP)
    cur = conn.cursor()
    try:
        query = f"SELECT id, razao_social, cnpj, contrato_mensal FROM clientes_vip WHERE razao_social LIKE '%{q}%'"
        cur.execute(query)
        rows = cur.fetchall()
        COUNTERS["accepted_packets"] += 1
        log_security_event(f"[⚠️ ALERTA SQLi] Dados confidenciais extraídos via SQL Injection (Firewall Desativado)!")
        return {"query_executed": query, "results": rows, "status": "Vulnerable Query Executed"}
    except Exception as e:
        return {"error": str(e), "query_executed": query}
    finally:
        conn.close()


@app.get("/api/erp/busca-segura")
def search_secure(q: str = ""):
    """Endpoint SEGURO protegido por consulta parametrizada (Prepared Statement)."""
    if not os.path.exists(DB_ERP):
        return {"error": "Banco não inicializado"}
    conn = sqlite3.connect(DB_ERP)
    cur = conn.cursor()
    try:
        query = "SELECT id, razao_social, cnpj, contrato_mensal FROM clientes_vip WHERE razao_social LIKE ?"
        cur.execute(query, (f"%{q}%",))
        rows = cur.fetchall()
        return {"query_executed": "SELECT ... WHERE razao_social LIKE ? (Parametrizada)", "results": rows, "status": "Secure Query"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()


@app.get("/api/erp/last-cracked")
def get_last_cracked():
    return LAST_CRACKED_CREDENTIALS


@app.post("/api/erp/login")
def erp_login(data: Dict[str, str]):
    """Endpoint de autenticação corporativa (Wellington ERP / TOTVS)."""
    global FIREWALL_ENABLED, EXPERIMENTAL_ENABLED, QUARANTINE_ACTIVE, LAST_CRACKED_CREDENTIALS

    is_redteam = data.get("client_mode") == "redteam"
    usuario = data.get("usuario", "").strip()
    senha = data.get("senha", "").strip()

    if is_redteam:
        if FIREWALL_ENABLED and QUARANTINE_ACTIVE:
            COUNTERS["blocked_quarantine"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event(f"[🚫 NFTABLES DROP] Força bruta em '{usuario}' descartada (IP em Quarentena).")
            raise HTTPException(
                status_code=403,
                detail="[NFTABLES FIREWALL DROP] Conexão barrada: IP do Red Team em Quarentena!"
            )
        if FIREWALL_ENABLED and EXPERIMENTAL_ENABLED:
            COUNTERS["blocked_bruteforce"] += 1
            COUNTERS["total_dropped"] += 1
            log_security_event(f"[🛡️ ANTI-BRUTEFORCE DROP] Tentativa de senha '{senha}' para '{usuario}' bloqueada pelo Firewall!")
            raise HTTPException(
                status_code=403,
                detail="[NFTABLES FIREWALL DROP] Força bruta interceptada pelo Firewall Ativo! (Desative o Firewall no Blue Team para permitir a quebra de senha)."
            )

    if not os.path.exists(DB_ERP):
        return {"success": False, "msg": "Banco corporativo não inicializado"}

    conn = sqlite3.connect(DB_ERP)
    cur = conn.cursor()
    cur.execute("SELECT id, usuario, cargo, departamento FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    row = cur.fetchone()
    conn.close()

    COUNTERS["accepted_packets"] += 1

    if row:
        LAST_CRACKED_CREDENTIALS = {
            "usuario": row[1],
            "senha": senha,
            "cargo": row[2],
            "departamento": row[3],
            "timestamp": time.time()
        }
        log_security_event(f"[🔓 CREDENCIAL CAPTURADA] Red Team descobriu a senha de '{row[1]}' ({row[2]}) com o Firewall Desativado!")
        return {
            "success": True,
            "usuario": row[1],
            "cargo": row[2],
            "depto": row[3],
            "msg": f"Autenticação corporativa aprovada. Bem-vindo, {row[1]}!"
        }

    log_security_event(f"[LOGIN FALHOU] Tentativa de força bruta recusada para '{usuario}' (senha '{senha}' incorreta).")
    return {"success": False, "msg": "Credenciais corporativas inválidas"}


# ==============================================================================
# TELEMETRIA DO SISTEMA E LOGS
# ==============================================================================
@app.get("/api/system/status")
def get_system_status() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory": {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "free_gb": round(mem.available / (1024**3), 2),
            "percent": mem.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        },
        "boot_time": psutil.boot_time()
    }


@app.get("/api/network/interfaces")
def get_network_interfaces() -> List[Dict[str, Any]]:
    interfaces = []
    net_if_addrs = psutil.net_if_addrs()
    net_if_stats = psutil.net_if_stats()

    for iface_name, addrs in net_if_addrs.items():
        stats = net_if_stats.get(iface_name)
        ip_v4 = [a.address for a in addrs if a.family.name == 'AF_INET']
        ip_v6 = [a.address for a in addrs if a.family.name == 'AF_INET6']
        interfaces.append({
            "name": iface_name,
            "is_up": stats.isup if stats else False,
            "speed_mbps": stats.speed if stats else 0,
            "ipv4": ip_v4,
            "ipv6": ip_v6
        })
    return interfaces


@app.get("/api/services/status")
def get_services_status() -> Dict[str, Dict[str, Any]]:
    results = {}
    for service in SERVICES:
        try:
            res = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True,
                check=False
            )
            is_active = (res.stdout.strip() == "active")
            results[service] = {
                "active": is_active,
                "raw_state": res.stdout.strip()
            }
        except Exception as e:
            results[service] = {
                "active": False,
                "error": str(e)
            }
    return results


@app.get("/api/logs/nginx")
def get_nginx_logs(lines: int = 50) -> Dict[str, List[str]]:
    return {"file": "SOC Security & Firewall Event Stream", "lines": SECURITY_EVENTS[-lines:]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
