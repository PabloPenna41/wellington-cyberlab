#!/usr/bin/env python3
"""
Wellington CyberLab — Blue Team Control Center (Servidor CachyOS)
Interface Gráfica de Segurança Defensiva, Hardening e Monitoramento (SOC)
Identidade Visual: BLUE TEAM / Deep Sapphire & Cybernetic Cyan
Didática interativa: explica mecanismos de defesa, filtragem e contenção.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
import psutil
import shutil
import json
import socket
import urllib.request

def get_local_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

LAB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def open_browser(url):
    for prog in ["zen-browser", "firefox", "brave", "chromium", "google-chrome-stable", "xdg-open"]:
        if shutil.which(prog):
            try:
                subprocess.Popen([prog, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                return True
            except Exception:
                continue
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass


# ==============================================================================
# Paleta de Cores: BLUE TEAM (Defensivo / Safira Profunda / Ciano Cyber)
# ==============================================================================
BLUE_THEME = {
    "bg_dark": "#070c18",        # Fundo ultra escuro azulado
    "bg_panel": "#0c1527",       # Painéis elevados
    "bg_card": "#13213a",        # Cards e caixas de status
    "border": "#1e3256",         # Borda sutil azulada
    "text_main": "#e2e8f0",      # Texto principal de alta legibilidade
    "text_muted": "#8da4c4",     # Texto secundário
    "accent_blue": "#38bdf8",    # Azul celeste vibrante (Blue Team)
    "accent_cyan": "#06b6d4",    # Ciano defensivo
    "accent_green": "#10b981",   # Status seguro / Protegido
    "accent_amber": "#f59e0b",   # Alerta de segurança
    "accent_red": "#f43f5e",     # Bloqueio / Violação
    "code_bg": "#050912",        # Fundo do console defensivo
    "code_fg": "#7dd3fc"         # Texto de telemetria
}

class BlueTeamControlCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wellington CyberLab — Blue Team Control Center [DEFENSIVE SOC]")
        self.geometry("1140x780")
        self.minsize(980, 680)
        self.configure(bg=BLUE_THEME["bg_dark"])

        self.setup_styles()
        self.create_header()
        self.create_notebook()
        self.create_footer()

        # Telemetria periódica
        self.running = True
        self.telemetry_thread = threading.Thread(target=self.update_telemetry_loop, daemon=True)
        self.telemetry_thread.start()

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BLUE_THEME["bg_dark"], borderwidth=0)
        style.configure("TNotebook.Tab", background=BLUE_THEME["bg_panel"], foreground=BLUE_THEME["text_muted"],
                        padding=[14, 8], font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", BLUE_THEME["bg_card"])],
                  foreground=[("selected", BLUE_THEME["accent_blue"])])

    def create_header(self):
        header = tk.Frame(self, bg=BLUE_THEME["bg_panel"], height=70, padx=20, pady=10)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Esquerda: Identidade BLUE TEAM
        left_box = tk.Frame(header, bg=BLUE_THEME["bg_panel"])
        left_box.pack(side="left")

        title_row = tk.Frame(left_box, bg=BLUE_THEME["bg_panel"])
        title_row.pack(anchor="w")

        lbl_badge = tk.Label(title_row, text=" 🛡️ BLUE TEAM ", font=("Helvetica", 9, "bold"),
                             fg="#ffffff", bg="#0284c7", padx=6, pady=2)
        lbl_badge.pack(side="left", padx=(0, 10))

        lbl_title = tk.Label(title_row, text="DEFENSIVE OPERATIONS CENTER (SOC HOST)",
                             font=("Helvetica", 13, "bold"), fg=BLUE_THEME["accent_blue"], bg=BLUE_THEME["bg_panel"])
        lbl_title.pack(side="left")

        lbl_sub = tk.Label(left_box,
                           text="Fortaleza do Laboratório: CachyOS Linux | Firewall Nftables | IDS Suricata | VPN WireGuard",
                           font=("Helvetica", 9), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Direita: Indicador de Proteção Global & Botão para Lançar Red Team
        right_box = tk.Frame(header, bg=BLUE_THEME["bg_panel"])
        right_box.pack(side="right")

        btn_launch_red = tk.Button(right_box, text="⚔️ Abrir Red Team Station", bg="#241313",
                                   fg="#ef4444", font=("Helvetica", 9, "bold"), padx=10, pady=5,
                                   borderwidth=1, cursor="hand2", command=self.launch_red_team_window)
        btn_launch_red.pack(side="right", padx=(10, 0))

        self.lbl_global_status = tk.Label(right_box, text="● DEFESA ATIVA", font=("Helvetica", 9, "bold"),
                                          fg=BLUE_THEME["accent_green"], bg=BLUE_THEME["bg_panel"])
        self.lbl_global_status.pack(side="right")

    def launch_red_team_window(self):
        script = os.path.join(LAB_DIR, "gui", "red_team_station.py")
        try:
            subprocess.Popen([sys.executable, script])
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao iniciar Red Team: {e}")

    def create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_dashboard = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])
        self.tab_services = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])
        self.tab_firewall = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])
        self.tab_network = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])
        self.tab_academy = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])
        self.tab_setup = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])
        self.tab_logs = tk.Frame(self.notebook, bg=BLUE_THEME["bg_dark"])

        self.notebook.add(self.tab_dashboard, text=" 📊 Painel de Defesa (Dashboard) ")
        self.notebook.add(self.tab_services, text=" ⚙️ Serviços & Hardening ")
        self.notebook.add(self.tab_firewall, text=" 🛡️ Firewall Nftables Modular ")
        self.notebook.add(self.tab_network, text=" 🌐 Topologia de Rede & VPN ")
        self.notebook.add(self.tab_academy, text=" 📚 Teoria de Defesa & Didática ")
        self.notebook.add(self.tab_setup, text=" 🚀 Assistente de Provisionamento ")
        self.notebook.add(self.tab_logs, text=" 📜 Logs do SOC em Tempo Real ")

        self.build_dashboard_tab()
        self.build_services_tab()
        self.build_firewall_tab()
        self.build_network_tab()
        self.build_academy_tab()
        self.build_setup_tab()
        self.build_logs_tab()

    # ==========================================================================
    # ABA 1: DASHBOARD DEFENSIVO
    # ==========================================================================
    def build_dashboard_tab(self):
        container = tk.Frame(self.tab_dashboard, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        cards_row = tk.Frame(container, bg=BLUE_THEME["bg_dark"])
        cards_row.pack(fill="x", pady=(0, 15))

        self.card_cpu = self.create_metric_card(cards_row, "CARGA DO PROCESSADOR", "0.0%", "13th Gen Intel i5-1335U")
        self.card_cpu.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.card_ram = self.create_metric_card(cards_row, "MEMÓRIA RAM DISPONÍVEL", "0.0 / 0.0 GB", "ZRAM comprimido ativo")
        self.card_ram.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.card_disk = self.create_metric_card(cards_row, "ARMAZENAMENTO SEGURO", "0.0 / 0.0 GB", "Partição NVMe Btrfs /")
        self.card_disk.pack(side="left", fill="both", expand=True)

        bottom_row = tk.Frame(container, bg=BLUE_THEME["bg_dark"])
        bottom_row.pack(fill="both", expand=True)

        # Painel esquerdo: Vetores e Endereços Protegidos
        info_panel = tk.Frame(bottom_row, bg=BLUE_THEME["bg_panel"], padx=15, pady=15,
                              highlightbackground=BLUE_THEME["border"], highlightthickness=1)
        info_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(info_panel, text="PERÍMETROS DEFENSIVOS E INTERFACES", font=("Helvetica", 11, "bold"),
                 fg=BLUE_THEME["accent_cyan"], bg=BLUE_THEME["bg_panel"]).pack(anchor="w", pady=(0, 10))

        self.lbl_ip_local = tk.Label(info_panel, text=f"Interface Wi-Fi (wlan0): {get_local_lan_ip()}/24 [Perímetro Local]",
                                     font=("Helvetica", 10), fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_panel"])
        self.lbl_ip_local.pack(anchor="w", pady=3)

        self.lbl_ip_vpn = tk.Label(info_panel, text="Interface VPN (wg0): 10.77.0.1 [Zona Criptografada ChaCha20]",
                                   font=("Helvetica", 10), fg=BLUE_THEME["accent_blue"], bg=BLUE_THEME["bg_panel"])
        self.lbl_ip_vpn.pack(anchor="w", pady=3)

        self.lbl_client_win = tk.Label(info_panel, text="Estação de Auditoria (Red Team): 10.77.0.2 [Acesso Monitorado]",
                                       font=("Helvetica", 10), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        self.lbl_client_win.pack(anchor="w", pady=3)

        self.lbl_active_conns = tk.Label(info_panel, text="Sessões de rede ativas (Conntrack): Calculando...",
                                         font=("Helvetica", 10), fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_panel"])
        self.lbl_active_conns.pack(anchor="w", pady=3)

        # Painel direito: Wellington Negócios e Status Web
        web_panel = tk.Frame(bottom_row, bg=BLUE_THEME["bg_panel"], padx=15, pady=15,
                             highlightbackground=BLUE_THEME["border"], highlightthickness=1)
        web_panel.pack(side="right", fill="both", expand=True)

        tk.Label(web_panel, text="PORTAL INSTITUCIONAL WELLINGTON NEGÓCIOS", font=("Helvetica", 11, "bold"),
                 fg=BLUE_THEME["accent_blue"], bg=BLUE_THEME["bg_panel"]).pack(anchor="w", pady=(0, 10))

        tk.Label(web_panel,
                 text="Ambiente Público Estático e Auditado:\n"
                      "Ativo em: http://localhost:8000 (API Host) e Porta 80 (Nginx)\n"
                      "Headers Defensivos: X-Frame-Options, X-Content-Type-Options ativos.",
                 font=("Helvetica", 9), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"], justify="left").pack(anchor="w", pady=(0, 15))

        btn_open = tk.Button(web_panel, text="🌐 Acessar Portal Institucional Seguro (Porta 8000)",
                             bg="#0284c7", fg="#ffffff", font=("Helvetica", 10, "bold"),
                             padx=12, pady=7, borderwidth=0, cursor="hand2",
                             command=lambda: open_browser("http://127.0.0.1:8000/"))
        btn_open.pack(anchor="w")

    def create_metric_card(self, parent, title, main_val, sub_val):
        card = tk.Frame(parent, bg=BLUE_THEME["bg_panel"], padx=15, pady=12,
                        highlightbackground=BLUE_THEME["border"], highlightthickness=1)
        tk.Label(card, text=title, font=("Helvetica", 8, "bold"), fg=BLUE_THEME["text_muted"],
                 bg=BLUE_THEME["bg_panel"]).pack(anchor="w")
        lbl_main = tk.Label(card, text=main_val, font=("Helvetica", 18, "bold"),
                            fg=BLUE_THEME["accent_blue"], bg=BLUE_THEME["bg_panel"])
        lbl_main.pack(anchor="w", pady=4)
        lbl_sub = tk.Label(card, text=sub_val, font=("Helvetica", 8),
                           fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        lbl_sub.pack(anchor="w")
        card.lbl_main = lbl_main
        card.lbl_sub = lbl_sub
        return card

    # ==========================================================================
    # ABA 2: SERVIÇOS & HARDENING
    # ==========================================================================
    def build_services_tab(self):
        container = tk.Frame(self.tab_services, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="ESTADO E CONTROLE DAS DEFESAS DO SERVIDOR", font=("Helvetica", 12, "bold"),
                 fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_dark"]).pack(anchor="w", pady=(0, 10))

        self.service_cards = {}
        services_to_track = [
            ("nginx", "Nginx Web Server (Proxy Reverso & Site Institucional)", "Protege o backend e entrega arquivos estáticos com cabeçalhos de segurança."),
            ("ufw", "UFW Firewall (Camada Temporária de Filtragem)", "Mantém a política padrão restritiva de entrada enquanto preparamos a Fase 2."),
            ("nftables", "Nftables Engine (Firewall Principal Modular)", "Motor nativo do kernel Linux para separação de regras essenciais e experimentais."),
            ("suricata", "Suricata IDS/IPS (Sistema de Detecção de Intrusões)", "Inspeção profunda de pacotes (DPI) para identificar varreduras e tentativas de ataque."),
            ("wg-quick@wg0", "WireGuard VPN (Túnel Criptografado 10.77.0.1)", "Garante que serviços vulneráveis e administrativos só sejam acessíveis via VPN.")
        ]

        for s_name, s_label, s_desc in services_to_track:
            card = self.create_service_card(container, s_name, s_label, s_desc)
            card.pack(fill="x", pady=5)
            self.service_cards[s_name] = card

    def create_service_card(self, parent, service_name, display_name, desc_text):
        row = tk.Frame(parent, bg=BLUE_THEME["bg_panel"], padx=15, pady=10,
                       highlightbackground=BLUE_THEME["border"], highlightthickness=1)

        lbl_dot = tk.Label(row, text="●", font=("Helvetica", 14), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        lbl_dot.pack(side="left", padx=(0, 10))

        info_frame = tk.Frame(row, bg=BLUE_THEME["bg_panel"])
        info_frame.pack(side="left", fill="both", expand=True)

        lbl_name = tk.Label(info_frame, text=display_name, font=("Helvetica", 10, "bold"),
                            fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_panel"])
        lbl_name.pack(anchor="w")

        lbl_desc = tk.Label(info_frame, text=desc_text, font=("Helvetica", 8),
                            fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        lbl_desc.pack(anchor="w", pady=(2, 2))

        lbl_status = tk.Label(info_frame, text="Status: Inspecionando...", font=("Helvetica", 8, "bold"),
                              fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        lbl_status.pack(anchor="w")

        btn_start = tk.Button(row, text="Iniciar Defesa", bg=BLUE_THEME["bg_card"], fg=BLUE_THEME["accent_green"],
                              font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=1, cursor="hand2",
                              command=lambda: self.run_systemctl(service_name, "start"))
        btn_start.pack(side="right", padx=4)

        btn_stop = tk.Button(row, text="Interromper", bg=BLUE_THEME["bg_card"], fg=BLUE_THEME["accent_red"],
                             font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=1, cursor="hand2",
                             command=lambda: self.run_systemctl(service_name, "stop"))
        btn_stop.pack(side="right", padx=4)

        row.lbl_dot = lbl_dot
        row.lbl_status = lbl_status
        return row

    def run_systemctl(self, service, action):
        def task():
            cmd = f"pkexec systemctl {action} {service}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("Sucesso", f"Serviço defensivo {service} [{action}] executado!")
            else:
                messagebox.showerror("Erro de Privilégio", f"Falha ao executar: {res.stderr or res.stdout}")
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # ABA 3: FIREWALL NFTABLES MODULAR
    # ==========================================================================
    def build_firewall_tab(self):
        container = tk.Frame(self.tab_firewall, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Painel Superior: Demonstrações Práticas de Defesa (Didática Interativa)
        demo_card = tk.Frame(container, bg=BLUE_THEME["bg_panel"], padx=15, pady=12,
                             highlightbackground=BLUE_THEME["border"], highlightthickness=1)
        demo_card.pack(fill="x", pady=(0, 15))

        tk.Label(demo_card, text="LABORATÓRIO DE DEMONSTRAÇÕES PRÁTICAS DO FIREWALL (NFTABLES)",
                 font=("Helvetica", 11, "bold"), fg=BLUE_THEME["accent_cyan"], bg=BLUE_THEME["bg_panel"]).pack(anchor="w", pady=(0, 4))

        tk.Label(demo_card,
                 text="Alterne os estados do firewall com 1 clique para demonstrar aos alunos/ouvintes como o kernel do Linux\n"
                      "bloqueia ataques em tempo real, sem jamais perder o acesso administrativo:",
                 font=("Helvetica", 9), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"], justify="left").pack(anchor="w", pady=(0, 10))

        # Linha 1: CONTROLE GERAL DO FIREWALL (LIGA / DESLIGA)
        master_row = tk.Frame(demo_card, bg=BLUE_THEME["bg_panel"])
        master_row.pack(fill="x", pady=(0, 10))

        tk.Label(master_row, text="ESTADO GERAL:", font=("Helvetica", 9, "bold"),
                 fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_panel"]).pack(side="left")

        btn_disable_all = tk.Button(master_row, text="🔴 DESATIVAR FIREWALL COMPLETAMENTE (Modo Aberto)",
                                    bg="#dc2626", fg="#ffffff", font=("Helvetica", 8, "bold"),
                                    padx=12, pady=6, borderwidth=0, cursor="hand2",
                                    command=self.disable_all_firewall)
        btn_disable_all.pack(side="left", padx=(8, 6))

        btn_enable_all = tk.Button(master_row, text="🟢 ATIVAR / RESTAURAR FIREWALL (Modo Blindado)",
                                   bg="#059669", fg="#ffffff", font=("Helvetica", 8, "bold"),
                                   padx=12, pady=6, borderwidth=0, cursor="hand2",
                                   command=self.enable_all_firewall)
        btn_enable_all.pack(side="left", padx=(0, 10))

        self.lbl_fw_master_badge = tk.Label(master_row, text="● FIREWALL: ATIVO / PROTEGIDO",
                                            font=("Helvetica", 9, "bold"), fg="#10b981", bg=BLUE_THEME["bg_panel"])
        self.lbl_fw_master_badge.pack(side="right")

        # Linha 2: Tabelas Modulares do Nftables
        btn_grid = tk.Frame(demo_card, bg=BLUE_THEME["bg_panel"])
        btn_grid.pack(fill="x", pady=(0, 8))

        tk.Label(btn_grid, text="Regras Modulares:", font=("Helvetica", 9, "bold"),
                 fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_panel"]).pack(side="left")

        btn_perm = tk.Button(btn_grid, text="🛡️ Carregar Só Permanentes", bg="#0284c7", fg="#ffffff",
                             font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=0, cursor="hand2",
                             command=self.load_permanent_only)
        btn_perm.pack(side="left", padx=(8, 6))

        btn_exp = tk.Button(btn_grid, text="⚡ Ativar Experimentais (Anti-BruteForce / Rate-Limit)", bg="#d97706", fg="#ffffff",
                            font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=0, cursor="hand2",
                            command=self.enable_experimental_rules)
        btn_exp.pack(side="left", padx=(0, 6))

        btn_reset = tk.Button(btn_grid, text="🧹 Limpar Experimentais", bg="#475569", fg="#ffffff",
                              font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=0, cursor="hand2",
                              command=self.disable_experimental_rules)
        btn_reset.pack(side="left")

        # Linha 3: Bloqueio dinâmico do Red Team ao Site e Serviços
        ip_row = tk.Frame(demo_card, bg=BLUE_THEME["bg_panel"])
        ip_row.pack(fill="x", pady=(0, 0))

        tk.Label(ip_row, text="Ações de Quarentena:", font=("Helvetica", 9, "bold"),
                 fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_panel"]).pack(side="left")

        btn_block_site = tk.Button(ip_row, text="🚫 BLOQUEAR SITE PARA O RED TEAM", bg="#991b1b", fg="#ffffff",
                                   font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=0, cursor="hand2",
                                   command=self.block_redteam_from_site)
        btn_block_site.pack(side="left", padx=(8, 6))

        btn_unblock_site = tk.Button(ip_row, text="✅ LIBERAR SITE PARA O RED TEAM", bg="#059669", fg="#ffffff",
                                     font=("Helvetica", 8, "bold"), padx=10, pady=5, borderwidth=0, cursor="hand2",
                                     command=self.unblock_redteam_from_site)
        btn_unblock_site.pack(side="left")

        self.lbl_fw_status_badge = tk.Label(ip_row, text="● Red Team: LIBERADO NO SITE PÚBLICO", font=("Helvetica", 8, "bold"),
                                            fg=BLUE_THEME["accent_green"], bg=BLUE_THEME["bg_panel"])
        self.lbl_fw_status_badge.pack(side="right")

        # Terminal de Visualização das Regras e Contadores
        top_bar = tk.Frame(container, bg=BLUE_THEME["bg_dark"])
        top_bar.pack(fill="x", pady=(10, 5))

        tk.Label(top_bar, text="CONJUNTO DE REGRAS E CONTADORES EM TEMPO REAL (NFTABLES RULESET & EVENTOS SOC):",
                 font=("Helvetica", 10, "bold"), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_dark"]).pack(side="left")

        btn_inspect = tk.Button(top_bar, text="🔄 Atualizar Contadores Agora", bg=BLUE_THEME["bg_card"],
                                fg=BLUE_THEME["accent_blue"], font=("Helvetica", 8, "bold"), padx=8, pady=4,
                                borderwidth=1, cursor="hand2", command=self.inspect_firewall)
        btn_inspect.pack(side="right", padx=(6, 0))

        btn_kernel_sync = tk.Button(top_bar, text="🔐 Aplicar no Kernel Linux (pkexec)", bg=BLUE_THEME["bg_card"],
                                    fg=BLUE_THEME["text_muted"], font=("Helvetica", 8), padx=8, pady=4,
                                    borderwidth=1, cursor="hand2", command=lambda: self.run_firewall_toggle("load-permanent"))
        btn_kernel_sync.pack(side="right")

        self.txt_firewall = scrolledtext.ScrolledText(container, bg=BLUE_THEME["code_bg"], fg=BLUE_THEME["code_fg"],
                                                      font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_firewall.pack(fill="both", expand=True)
        self.inspect_firewall()

    def sync_badges_from_state(self, state_data):
        fw_on = state_data.get("firewall_enabled", True)
        exp_on = state_data.get("experimental_enabled", True)
        quar_on = state_data.get("quarantine_active", False)

        if not fw_on:
            self.lbl_fw_master_badge.config(text="● FIREWALL: DESATIVADO / MODO ABERTO", fg="#ef4444")
            self.lbl_global_status.config(text="● FIREWALL DESLIGADO (VULNERÁVEL)", fg="#ef4444")
            self.lbl_fw_status_badge.config(text="● Red Team: TOTALMENTE LIBERADO (SEM PROTEÇÃO)", fg="#f59e0b")
        elif quar_on:
            self.lbl_fw_master_badge.config(text="● FIREWALL: ATIVO / QUARENTENA MÁXIMA", fg="#10b981")
            self.lbl_global_status.config(text="● DEFESA ATIVA (QUARENTENA)", fg="#10b981")
            self.lbl_fw_status_badge.config(text="● Red Team: BLOQUEADO NO SITE E ERP (DROP)", fg=BLUE_THEME["accent_red"])
        elif exp_on:
            self.lbl_fw_master_badge.config(text="● FIREWALL: ATIVO / BLINDADO (PERM + EXP)", fg="#10b981")
            self.lbl_global_status.config(text="● DEFESA ATIVA (BLINDADO)", fg="#10b981")
            self.lbl_fw_status_badge.config(text="● Red Team: SITE LIBERADO | ATAQUES ERP BLOQUEADOS", fg=BLUE_THEME["accent_green"])
        else:
            self.lbl_fw_master_badge.config(text="● FIREWALL: ATIVO (SÓ PERMANENTES)", fg="#38bdf8")
            self.lbl_global_status.config(text="● DEFESA PARCIAL (SÓ PERM)", fg="#38bdf8")
            self.lbl_fw_status_badge.config(text="● Red Team: LIBERADO (REGRAS EXP. DESATIVADAS)", fg="#f59e0b")

    def disable_all_firewall(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/toggle-all?enable=false", timeout=1.5)
        except Exception as e:
            messagebox.showerror("Erro de Comunicação", f"Não foi possível contatar o motor do Firewall: {e}")
            return
        self.inspect_firewall()
        messagebox.showwarning(
            "Firewall Nftables Desativado",
            "🔴 O FIREWALL FOI COMPLETAMENTE DESATIVADO (MODO ABERTO)!\n\n"
            "• Site Principal: LIBERADO para o Red Team\n"
            "• Força Bruta no Login do TOTVS: LIBERADA (Vulnerável a quebra de senha)\n"
            "• Injeção SQLi no ERP: LIBERADA (Vulnerável a vazamento de dados)\n"
            "• Flood Anti-DoS: SEM LIMITE DE TAXA"
        )

    def enable_all_firewall(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/toggle-all?enable=true", timeout=1.5)
        except Exception as e:
            messagebox.showerror("Erro de Comunicação", f"Não foi possível contatar o motor do Firewall: {e}")
            return
        self.inspect_firewall()
        messagebox.showinfo(
            "Firewall Nftables Ativado",
            "🟢 O FIREWALL FOI ATIVADO E RESTAURADO (MODO BLINDADO)!\n\n"
            "• Regras Permanentes e Experimentais carregadas.\n"
            "• Ataques de Força Bruta, SQL Injection e Flood DoS do Red Team agora serão interceptados e bloqueados!\n"
            "• O Site Público continua acessível até que você acione a Quarentena."
        )

    def load_permanent_only(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/toggle-all?enable=true", timeout=1.5)
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/experimental/toggle?enable=false", timeout=1.5)
        except Exception:
            pass
        self.inspect_firewall()
        messagebox.showinfo("Nftables Modular", "🛡️ Apenas a tabela 'wellington_permanent' está ativa.\nAs regras experimentais de bloqueio de ataques de camada 7 foram descarregadas.")

    def enable_experimental_rules(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/experimental/toggle?enable=true", timeout=1.5)
        except Exception:
            pass
        self.inspect_firewall()
        messagebox.showinfo("Nftables Modular", "⚡ Tabela 'wellington_experimental' ATIVADA!\nProteções contra Força Bruta, SQL Injection e Rate-Limit Anti-DoS estão em vigor.")

    def disable_experimental_rules(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/experimental/toggle?enable=false", timeout=1.5)
        except Exception:
            pass
        self.inspect_firewall()
        messagebox.showwarning("Nftables Modular", "🧹 Tabela 'wellington_experimental' REMOVIDA!\nAs proteções contra Força Bruta, SQLi e Rate-Limit foram desligadas (apenas regras permanentes ativas).")

    def block_redteam_from_site(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/quarantine/toggle?enable=true", timeout=1.5)
        except Exception:
            pass
        self.inspect_firewall()
        messagebox.showwarning(
            "Quarentena Ativada (DROP)",
            "🚫 ACESSO DO RED TEAM TOTALMENTE BLOQUEADO!\n\n"
            "O IP do Red Team foi inserido no conjunto '@redteam_blacklist'.\n"
            "• Site Principal: BLOQUEADO (403 DROP)\n"
            "• Força Bruta / SQLi / Flood: BLOQUEADOS (403 DROP)"
        )

    def unblock_redteam_from_site(self):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/quarantine/toggle?enable=false", timeout=1.5)
        except Exception:
            pass
        self.inspect_firewall()
        messagebox.showinfo(
            "Quarentena Removida",
            "✅ ACESSO DO RED TEAM AO SITE PRINCIPAL LIBERADO!\n\n"
            "O Red Team já pode abrir e visualizar o site institucional da Wellington Negócios normalmente!"
        )

    def inspect_firewall(self):
        def task():
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/state", timeout=1.5) as r_state:
                    state_data = json.loads(r_state.read().decode("utf-8"))
                with urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/ruleset", timeout=1.5) as r_rules:
                    rules_data = json.loads(r_rules.read().decode("utf-8"))

                def update_fw_ui():
                    self.sync_badges_from_state(state_data)
                    self.txt_firewall.delete("1.0", tk.END)
                    self.txt_firewall.insert(tk.END, rules_data.get("ruleset", ""))
                    events = rules_data.get("events", [])
                    if events:
                        self.txt_firewall.insert(tk.END, "\n# === ÚLTIMOS EVENTOS DE FILTRAGEM E SEGURANÇA (TEMPO REAL) ===\n")
                        for ev in events[-10:]:
                            self.txt_firewall.insert(tk.END, f"{ev}\n")
                self.after(0, update_fw_ui)
            except Exception as e:
                pass
        threading.Thread(target=task, daemon=True).start()

    def run_firewall_toggle(self, action, param=None):
        script = os.path.join(LAB_DIR, "firewall", "scripts", "toggle_experimental.sh")
        cmd = f"pkexec bash {script} {action}"
        if param:
            cmd += f" {param}"

        def task():
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            self.inspect_firewall()
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # ABA 4: REDE & TOPOLOGIA
    # ==========================================================================
    def build_network_tab(self):
        container = tk.Frame(self.tab_network, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg=BLUE_THEME["bg_dark"])
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="TOPOLOGIA DE REDES LOCAIS E TÚNEIS", font=("Helvetica", 11, "bold"),
                 fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_dark"]).pack(side="left")

        btn_refresh = tk.Button(header, text="🔄 Atualizar Roteamento", bg=BLUE_THEME["bg_card"],
                                fg=BLUE_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=8, pady=4,
                                borderwidth=1, cursor="hand2", command=self.refresh_network)
        btn_refresh.pack(side="right")

        self.txt_network = scrolledtext.ScrolledText(container, bg=BLUE_THEME["code_bg"], fg=BLUE_THEME["code_fg"],
                                                     font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_network.pack(fill="both", expand=True)
        self.refresh_network()

    def refresh_network(self):
        self.txt_network.delete("1.0", tk.END)
        out = subprocess.run(["ip", "-br", "addr"], capture_output=True, text=True).stdout
        routes = subprocess.run(["ip", "route"], capture_output=True, text=True).stdout
        self.txt_network.insert(tk.END, "=== INTERFACES FÍSICAS E VIRTUAIS (ip -br addr) ===\n" + out + "\n")
        self.txt_network.insert(tk.END, "=== TABELA DE ROTEAMENTO DO SERVIDOR (ip route) ===\n" + routes)

    # ==========================================================================
    # ABA 5: DIDÁTICA E TEORIA DE DEFESA
    # ==========================================================================
    def build_academy_tab(self):
        container = tk.Frame(self.tab_academy, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        txt_academy = scrolledtext.ScrolledText(container, bg=BLUE_THEME["bg_panel"], fg=BLUE_THEME["text_main"],
                                                font=("Helvetica", 10), borderwidth=0, padx=15, pady=15)
        txt_academy.pack(fill="both", expand=True)

        content = """
================================================================================
          WELLINGTON CYBERLAB — CADERNO DIDÁTICO DE DEFESA & BLUE TEAM
================================================================================

🛡️ O PAPEL DO BLUE TEAM:
O Blue Team é a força de defesa responsável pela proteção dos ativos digitais,
detecção precoce de anomalias, análise forense e endurecimento contínuo (hardening)
da infraestrutura do Wellington CyberLab.

--------------------------------------------------------------------------------
1. COMO FUNCIONA O FIREWALL MODULAR (NFTABLES):
--------------------------------------------------------------------------------
- Stateful Firewall (Conntrack): O kernel inspeciona o estado da conexão. Pacotes
  que pertencem a conexões já aprovadas são aceitos automaticamente:
  'ct state { established, related } accept'.
- Separação entre Regras Permanentes e Experimentais:
  * Regras Permanentes: Garantem acesso SSH administrativo, tráfego de loopback
    essencial e integridade dos serviços críticos. Jamais são desligadas.
  * Regras Experimentais: Regras criadas para exercícios práticos (ex: bloquear um IP
    específico do Red Team, limitar taxa de requisições SYN). Podem ser desativadas
    com um único comando sem causar *lockout* (perda de acesso ao servidor).

--------------------------------------------------------------------------------
2. PAPEL DO SURICATA COMO IDS/IPS:
--------------------------------------------------------------------------------
- Deep Packet Inspection (DPI): Enquanto o firewall analisa apenas IPs e portas
  (Camadas 3 e 4), o Suricata analisa o conteúdo do pacote (Camadas 4 a 7).
- Detecção de Assinaturas: Ao receber requisições do Red Team contendo injeções
  SQL (' OR '1'='1) ou varreduras Nmap, o Suricata gera alertas no arquivo
  /var/log/suricata/fast.log identificando o atacante e a severidade da ameaça.

--------------------------------------------------------------------------------
3. ISOLAMENTO CRIPTOGRÁFICO COM WIREGUARD:
--------------------------------------------------------------------------------
- As aplicações intencionalmente vulneráveis da Fase 4 do laboratório ficarão
  restritas à sub-rede 10.77.0.0/24. Isso garante que testes controlados possam
  ser executados pelo computador Windows através da VPN sem nunca expor falhas
  para a rede Wi-Fi local ou para a Internet pública!
================================================================================
"""
        txt_academy.insert(tk.END, content)
        txt_academy.config(state="disabled")

    # ==========================================================================
    # ABA 6: ASSISTENTE DE PROVISIONAMENTO (FASE 1)
    # ==========================================================================
    def build_setup_tab(self):
        container = tk.Frame(self.tab_setup, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        desc = tk.Frame(container, bg=BLUE_THEME["bg_panel"], padx=15, pady=12,
                        highlightbackground=BLUE_THEME["border"], highlightthickness=1)
        desc.pack(fill="x", pady=(0, 15))

        tk.Label(desc, text="PROVISIONAMENTO E VALIDAÇÃO DA FASE 1", font=("Helvetica", 11, "bold"),
                 fg=BLUE_THEME["accent_cyan"], bg=BLUE_THEME["bg_panel"]).pack(anchor="w")

        tk.Label(desc,
                 text="Execute o provisionamento automático para garantir que Nginx, arquivos em /srv/http e logs estejam em conformidade:",
                 font=("Helvetica", 9), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"]).pack(anchor="w", pady=(5, 10))

        btn_deploy = tk.Button(desc, text="⚡ EXECUTAR DEPLOY AUTOMÁTICO DA FASE 1", bg="#0284c7", fg="#ffffff",
                               font=("Helvetica", 10, "bold"), padx=15, pady=8, borderwidth=0, cursor="hand2",
                               command=self.run_setup_script)
        btn_deploy.pack(anchor="w")

        self.txt_setup_log = scrolledtext.ScrolledText(container, bg=BLUE_THEME["code_bg"], fg=BLUE_THEME["code_fg"],
                                                       font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_setup_log.pack(fill="both", expand=True)
        self.txt_setup_log.insert(tk.END, "Terminal de provisionamento pronto.\n")

    def run_setup_script(self):
        script_path = os.path.join(LAB_DIR, "firewall", "scripts", "setup_phase1.sh")
        self.txt_setup_log.delete("1.0", tk.END)
        self.txt_setup_log.insert(tk.END, f"[i] Iniciando provisionamento via pkexec: {script_path}\n")

        def task():
            try:
                proc = subprocess.Popen(["pkexec", "bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.txt_setup_log.insert(tk.END, line)
                    self.txt_setup_log.see(tk.END)
                proc.wait()
            except Exception as e:
                self.txt_setup_log.insert(tk.END, f"Erro: {e}\n")
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # ABA 7: LOGS DO SOC
    # ==========================================================================
    def build_logs_tab(self):
        container = tk.Frame(self.tab_logs, bg=BLUE_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        top = tk.Frame(container, bg=BLUE_THEME["bg_dark"])
        top.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="REGISTRO CENTRAL DE LOGS DE DEFESA (NGINX / UFW / SURICATA)", font=("Helvetica", 11, "bold"),
                 fg=BLUE_THEME["text_main"], bg=BLUE_THEME["bg_dark"]).pack(side="left")

        btn_refresh = tk.Button(top, text="🔄 Recarregar Registros", bg=BLUE_THEME["bg_card"],
                                fg=BLUE_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=8, pady=4,
                                borderwidth=1, cursor="hand2", command=self.refresh_logs)
        btn_refresh.pack(side="right")

        self.txt_logs = scrolledtext.ScrolledText(container, bg=BLUE_THEME["code_bg"], fg=BLUE_THEME["code_fg"],
                                                  font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_logs.pack(fill="both", expand=True)
        self.refresh_logs()

    def refresh_logs(self):
        self.txt_logs.delete("1.0", tk.END)
        found = False
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/state", timeout=1.0) as resp:
                state_data = json.loads(resp.read().decode("utf-8"))
                events = state_data.get("recent_events", [])
                if events:
                    found = True
                    self.txt_logs.insert(tk.END, "=== EVENTOS DE SEGURANÇA E FIREWALL EM TEMPO REAL (SOC STREAM) ===\n")
                    for ev in events:
                        self.txt_logs.insert(tk.END, f"{ev}\n")
                    self.txt_logs.insert(tk.END, "\n")
        except Exception:
            pass

        log_paths = [
            "/var/log/nginx/wellington_access.log",
            "/var/log/nginx/access.log",
            "/var/log/ufw.log",
            "/var/log/suricata/fast.log"
        ]
        for p in log_paths:
            if os.path.exists(p):
                found = True
                self.txt_logs.insert(tk.END, f"=== ARQUIVO DE AUDITORIA: {p} ===\n")
                try:
                    with open(p, "r") as f:
                        lines = f.readlines()[-30:]
                        self.txt_logs.insert(tk.END, "".join(lines) + "\n\n")
                except Exception as e:
                    self.txt_logs.insert(tk.END, f"Falha de leitura em {p}: {e}\n\n")
        if not found:
            self.txt_logs.insert(tk.END, "Aguardando novos eventos de tráfego dos serviços defensivos.\n")

    # ==========================================================================
    # TELEMETRIA EM TEMPO REAL
    # ==========================================================================
    def create_footer(self):
        footer = tk.Frame(self, bg=BLUE_THEME["bg_panel"], height=30, padx=15)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.lbl_footer = tk.Label(footer, text="Wellington CyberLab — Blue Team Control Center v2.0 | SOC Defense Mode",
                                   font=("Helvetica", 8), fg=BLUE_THEME["text_muted"], bg=BLUE_THEME["bg_panel"])
        self.lbl_footer.pack(side="left")

    def update_telemetry_loop(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                net_conns = len(psutil.net_connections())

                fw_state = None
                fw_rules = None
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/state", timeout=1.0) as r1:
                        fw_state = json.loads(r1.read().decode("utf-8"))
                    with urllib.request.urlopen("http://127.0.0.1:8000/api/firewall/ruleset", timeout=1.0) as r2:
                        fw_rules = json.loads(r2.read().decode("utf-8"))
                except Exception:
                    pass

                def update_ui():
                    self.card_cpu.lbl_main.config(text=f"{cpu}%")
                    self.card_ram.lbl_main.config(text=f"{round(mem.available/(1024**3), 1)} GB Livres")
                    self.card_disk.lbl_main.config(text=f"{round(disk.free/(1024**3), 1)} GB Livres")
                    self.lbl_active_conns.config(text=f"Sessões de rede ativas (Conntrack): {net_conns} conexões rastreadas")

                    if fw_state:
                        self.sync_badges_from_state(fw_state)
                    if fw_rules:
                        self.txt_firewall.delete("1.0", tk.END)
                        self.txt_firewall.insert(tk.END, fw_rules.get("ruleset", ""))
                        events = fw_rules.get("events", [])
                        if events:
                            self.txt_firewall.insert(tk.END, "\n# === ÚLTIMOS EVENTOS DE FILTRAGEM E SEGURANÇA (TEMPO REAL) ===\n")
                            for ev in events[-10:]:
                                self.txt_firewall.insert(tk.END, f"{ev}\n")

                    for s_name, card in self.service_cards.items():
                        res = subprocess.run(["systemctl", "is-active", s_name], capture_output=True, text=True)
                        state = res.stdout.strip()
                        if state == "active":
                            card.lbl_dot.config(fg=BLUE_THEME["accent_green"])
                            card.lbl_status.config(text=f"Status: Ativo e Protegendo (running)", fg=BLUE_THEME["accent_green"])
                        else:
                            card.lbl_dot.config(fg=BLUE_THEME["accent_red"])
                            card.lbl_status.config(text=f"Status: Inativo ({state})", fg=BLUE_THEME["text_muted"])

                self.after(0, update_ui)
            except Exception:
                pass
            time.sleep(2)

if __name__ == "__main__":
    app = BlueTeamControlCenter()
    app.mainloop()
