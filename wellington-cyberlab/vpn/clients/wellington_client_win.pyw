#!/usr/bin/env python3
"""
Wellington CyberLab — Red Team Client (Windows Station)
Interface Gráfica de Operações Ofensivas, Reconhecimento e Auditoria para Windows
Identidade Visual: RED TEAM / Crimson Cyberpunk
Didática interativa: explica conceitos de varredura e testes autorizados.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import os
import sys
import json
import urllib.request
import urllib.error
import webbrowser

RED_THEME = {
    "bg_dark": "#0f0808",
    "bg_panel": "#180d0d",
    "bg_card": "#241313",
    "border": "#3d1e1e",
    "text_main": "#fde8e8",
    "text_muted": "#a88282",
    "accent_red": "#ef4444",
    "accent_crimson": "#b91c1c",
    "accent_orange": "#f97316",
    "accent_amber": "#f59e0b",
    "accent_green": "#10b981",
    "code_bg": "#120707",
    "code_fg": "#fca5a5"
}

DEFAULT_CONFIG = {
    "lan_ip": "192.168.1.6",
    "vpn_ip": "10.77.0.1",
    "api_port": 8000,
    "web_port": 80,
    "active_mode": "LAN",
    "wireguard_tunnel_name": "wellington-lab"
}

CONFIG_FILE = "client_config.json"

class WellingtonRedTeamClientWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wellington CyberLab — Red Team Client [OFFENSIVE AUDIT / WINDOWS]")
        self.geometry("1100x740")
        self.minsize(960, 660)
        self.configure(bg=RED_THEME["bg_dark"])

        self.config_data = self.load_config()
        self.vpn_connected = False
        self.running = True

        self.setup_styles()
        self.create_header()
        self.create_notebook()
        self.create_footer()

        self.telemetry_thread = threading.Thread(target=self.telemetry_loop, daemon=True)
        self.telemetry_thread.start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config_data, f, indent=4)
        except Exception:
            pass

    def get_server_ip(self):
        return self.config_data["vpn_ip"] if self.config_data["active_mode"] == "VPN" else self.config_data["lan_ip"]

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=RED_THEME["bg_dark"], borderwidth=0)
        style.configure("TNotebook.Tab", background=RED_THEME["bg_panel"], foreground=RED_THEME["text_muted"],
                        padding=[14, 8], font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", RED_THEME["bg_card"])],
                  foreground=[("selected", RED_THEME["accent_red"])])

    def create_header(self):
        header = tk.Frame(self, bg=RED_THEME["bg_panel"], height=70, padx=20, pady=10)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=RED_THEME["bg_panel"])
        left.pack(side="left")

        row = tk.Frame(left, bg=RED_THEME["bg_panel"])
        row.pack(anchor="w")

        tk.Label(row, text=" 🎯 RED TEAM ", font=("Helvetica", 9, "bold"),
                 fg="#ffffff", bg=RED_THEME["accent_crimson"], padx=6, pady=2).pack(side="left", padx=(0, 10))

        tk.Label(row, text="OFFENSIVE AUDIT STATION (WINDOWS HOST)", font=("Helvetica", 13, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(side="left")

        self.lbl_sub = tk.Label(left, text=f"Alvo: {self.get_server_ip()} | Rota: {self.config_data['active_mode']} | Escopo: Laboratório Autorizado",
                                font=("Helvetica", 9), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"])
        self.lbl_sub.pack(anchor="w", pady=(2, 0))

        right = tk.Frame(header, bg=RED_THEME["bg_panel"])
        right.pack(side="right")

        self.btn_toggle_mode = tk.Button(right, text=f"Alternar p/ {'VPN' if self.config_data['active_mode'] == 'LAN' else 'LAN'}",
                                         bg=RED_THEME["bg_card"], fg=RED_THEME["accent_orange"], font=("Helvetica", 9, "bold"),
                                         padx=10, pady=5, borderwidth=1, cursor="hand2", command=self.toggle_mode)
        self.btn_toggle_mode.pack(side="right", padx=(10, 0))

        self.lbl_target_status = tk.Label(right, text="● SONDANDO SERVIDOR...", font=("Helvetica", 9, "bold"),
                                          fg=RED_THEME["accent_amber"], bg=RED_THEME["bg_panel"])
        self.lbl_target_status.pack(side="right")

    def toggle_mode(self):
        new_mode = "VPN" if self.config_data["active_mode"] == "LAN" else "LAN"
        self.config_data["active_mode"] = new_mode
        self.save_config()
        self.lbl_sub.config(text=f"Alvo: {self.get_server_ip()} | Rota: {new_mode} | Escopo: Laboratório Autorizado")
        self.btn_toggle_mode.config(text=f"Alternar p/ {'VPN' if new_mode == 'LAN' else 'LAN'}")
        messagebox.showinfo("Alvo Alterado", f"Alvo de testes alterado para: {new_mode}\nIP do Servidor: {self.get_server_ip()}")

    def create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_recon = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_vpn = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_web = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_academy = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_config = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])

        self.notebook.add(self.tab_recon, text=" 🎯 Red Team & Nmap Scanner ")
        self.notebook.add(self.tab_vpn, text=" 🔒 WireGuard VPN (10.77.0.2) ")
        self.notebook.add(self.tab_web, text=" 🌐 Wellington Negócios Alvos ")
        self.notebook.add(self.tab_academy, text=" 📚 Caderno Didático Ofensivo ")
        self.notebook.add(self.tab_config, text=" ⚙️ Configurações ")

        self.build_recon_tab()
        self.build_vpn_tab()
        self.build_web_tab()
        self.build_academy_tab()
        self.build_config_tab()

    def build_recon_tab(self):
        container = tk.Frame(self.tab_recon, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        ctrl = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=15, pady=12,
                        highlightbackground=RED_THEME["border"], highlightthickness=1)
        ctrl.pack(fill="x", pady=(0, 15))

        tk.Label(ctrl, text="TESTES AUTORIZADOS CONTRA O CACHYOS (BLUE TEAM)", font=("Helvetica", 11, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 6))

        btn_row = tk.Frame(ctrl, bg=RED_THEME["bg_panel"])
        btn_row.pack(fill="x")

        btn_fast = tk.Button(btn_row, text="⚡ Scan Portas Lab (80, 8000, 51820)", bg=RED_THEME["bg_card"],
                             fg=RED_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                             borderwidth=1, cursor="hand2", command=lambda: self.run_nmap("-p 80,443,8000,51820"))
        btn_fast.pack(side="left", padx=(0, 8))

        btn_svc = tk.Button(btn_row, text="🔬 Identificar Versões (-sV)", bg=RED_THEME["bg_card"],
                            fg=RED_THEME["accent_orange"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                            borderwidth=1, cursor="hand2", command=lambda: self.run_nmap("-sV -sC -p 80,8000"))
        btn_svc.pack(side="left", padx=(0, 8))

        btn_burp = tk.Button(btn_row, text="🦊 Burp Suite", bg=RED_THEME["bg_card"],
                             fg=RED_THEME["accent_amber"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                             borderwidth=1, cursor="hand2", command=self.open_burp)
        btn_burp.pack(side="left", padx=(0, 8))

        btn_wireshark = tk.Button(btn_row, text="🦈 Wireshark", bg=RED_THEME["bg_card"],
                                  fg=RED_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                                  borderwidth=1, cursor="hand2", command=self.open_wireshark)
        btn_wireshark.pack(side="left")

        self.txt_recon = scrolledtext.ScrolledText(container, bg=RED_THEME["code_bg"], fg=RED_THEME["code_fg"],
                                                  font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_recon.pack(fill="both", expand=True)
        self.txt_recon.insert(tk.END, "Console Red Team pronto. Dispare um scan para analisar as respostas do alvo.\n")

    def run_nmap(self, flags):
        target = self.get_server_ip()
        self.txt_recon.insert(tk.END, f"\n[!] Disparando Nmap {flags} contra {target}...\n{'-'*75}\n")
        self.txt_recon.see(tk.END)
        def task():
            cmd = f"nmap {flags} {target}"
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.txt_recon.insert(tk.END, line)
                    self.txt_recon.see(tk.END)
                proc.wait()
                self.txt_recon.insert(tk.END, "\n[✓] Varredura concluída!\n")
            except Exception as e:
                self.txt_recon.insert(tk.END, f"\n[X] Erro ao chamar Nmap: {e}\n")
        threading.Thread(target=task, daemon=True).start()

    def open_burp(self):
        try:
            subprocess.Popen(["BurpSuiteCommunity.exe"])
        except Exception:
            messagebox.showinfo("Burp Suite", "Burp Suite não localizado no PATH padrão do Windows.")

    def open_wireshark(self):
        try:
            subprocess.Popen(["wireshark.exe"])
        except Exception:
            messagebox.showinfo("Wireshark", "Wireshark não localizado no PATH padrão do Windows.")

    def build_vpn_tab(self):
        container = tk.Frame(self.tab_vpn, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=20, pady=20,
                        highlightbackground=RED_THEME["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="TÚNEL SEGURO WIREGUARD (CLIENTE WINDOWS)", font=("Helvetica", 12, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 8))

        tk.Label(card,
                 text="Permite alcançar os serviços do laboratório e a aplicação vulnerável de fora da rede local.\n"
                      "Esta Estação: 10.77.0.2/24 | Servidor: 10.77.0.1:51820",
                 font=("Helvetica", 9), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 15))

        self.btn_vpn = tk.Button(card, text="🔒 CONECTAR VPN WIREGUARD", bg=RED_THEME["accent_crimson"],
                                 fg="#ffffff", font=("Helvetica", 10, "bold"), padx=15, pady=8,
                                 borderwidth=0, cursor="hand2", command=self.toggle_vpn)
        self.btn_vpn.pack(anchor="w")

        self.txt_vpn = scrolledtext.ScrolledText(container, bg=RED_THEME["code_bg"], fg=RED_THEME["code_fg"],
                                                font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_vpn.pack(fill="both", expand=True)
        self.txt_vpn.insert(tk.END, "Status do Túnel WireGuard:\nAguardando inicialização.\n")

    def toggle_vpn(self):
        if not self.vpn_connected:
            cmd = 'wireguard.exe /installtunnelservice "C:\\WellingtonCyberLab\\vpn\\wellington-lab.conf"'
            self.txt_vpn.insert(tk.END, f"\n[+] Chamando WireGuard: {cmd}\n")
            self.vpn_connected = True
            self.btn_vpn.config(text="🔓 DESCONECTAR VPN WIREGUARD", bg=RED_THEME["accent_amber"])
        else:
            cmd = 'wireguard.exe /uninstalltunnelservice wellington-lab'
            self.txt_vpn.insert(tk.END, f"\n[-] Chamando WireGuard: {cmd}\n")
            self.vpn_connected = False
            self.btn_vpn.config(text="🔒 CONECTAR VPN WIREGUARD", bg=RED_THEME["accent_crimson"])

    def build_web_tab(self):
        container = tk.Frame(self.tab_web, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=20, pady=20,
                        highlightbackground=RED_THEME["border"], highlightthickness=1)
        card.pack(fill="x")

        tk.Label(card, text="ALVOS DA EMPRESA FICTÍCIA WELLINGTON NEGÓCIOS", font=("Helvetica", 12, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 10))

        # Alvo 1: Site Institucional
        r1 = tk.Frame(card, bg=RED_THEME["bg_panel"])
        r1.pack(fill="x", pady=6)
        tk.Label(r1, text="1. Site Institucional Público (Auditoria de Headers):", font=("Helvetica", 10, "bold"),
                 fg=RED_THEME["text_main"], bg=RED_THEME["bg_panel"]).pack(side="left")
        btn1 = tk.Button(r1, text="Abrir no Navegador", bg=RED_THEME["bg_card"], fg=RED_THEME["accent_orange"],
                         font=("Helvetica", 8, "bold"), padx=10, pady=4, borderwidth=1, cursor="hand2",
                         command=lambda: webbrowser.open(f"http://{self.get_server_ip()}:8000/"))
        btn1.pack(side="right")

        # Alvo 2: Vulnerável (Fase 4)
        r2 = tk.Frame(card, bg=RED_THEME["bg_panel"])
        r2.pack(fill="x", pady=6)
        tk.Label(r2, text="2. Aplicação Vulnerável (SQLi / XSS / Restrito VPN):", font=("Helvetica", 10, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(side="left")
        btn2 = tk.Button(r2, text="Abrir Ambiente Vulnerável", bg=RED_THEME["accent_crimson"], fg="#ffffff",
                         font=("Helvetica", 8, "bold"), padx=10, pady=4, borderwidth=0, cursor="hand2",
                         command=lambda: webbrowser.open(f"http://{self.get_server_ip()}:8000/vulnerable"))
        btn2.pack(side="right")

    def build_academy_tab(self):
        container = tk.Frame(self.tab_academy, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        txt = scrolledtext.ScrolledText(container, bg=RED_THEME["bg_panel"], fg=RED_THEME["text_main"],
                                       font=("Helvetica", 10), borderwidth=0, padx=15, pady=15)
        txt.pack(fill="both", expand=True)
        txt.insert(tk.END, """
================================================================================
          CADERNO DIDÁTICO: OPERAÇÕES DO RED TEAM (AUDITORIA OFENSIVA)
================================================================================

🎯 METODOLOGIA SEQUENCIAL DE AUDITORIA:
1. Reconhecimento Passivo e Ativo: Mapeamento de IPs, rotas e serviços abertos (Nmap).
2. Análise de Superfície de Ataque: Inspeção de cabeçalhos HTTP, portas e banners.
3. Teste de Injeção de Parâmetros: Testes de SQL Injection e validação deficiente de dados.
4. Comparação com o Blue Team: Verificar se o firewall Nftables barrou a requisição
   ou se o Suricata gerou alerta no fast.log.
================================================================================
""")
        txt.config(state="disabled")

    def build_config_tab(self):
        container = tk.Frame(self.tab_config, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        box = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=20, pady=20,
                       highlightbackground=RED_THEME["border"], highlightthickness=1)
        box.pack(fill="x")

        tk.Label(box, text="CONFIGURAÇÃO DE CONECTIVIDADE", font=("Helvetica", 11, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 10))

        tk.Label(box, text="IP Local do Servidor CachyOS (Modo LAN):", font=("Helvetica", 9),
                 fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"]).pack(anchor="w")
        self.entry_lan = tk.Entry(box, bg=RED_THEME["bg_dark"], fg=RED_THEME["text_main"], font=("Helvetica", 10))
        self.entry_lan.insert(0, self.config_data.get("lan_ip", "192.168.1.6"))
        self.entry_lan.pack(anchor="w", fill="x", pady=(2, 10))

        tk.Label(box, text="IP da VPN WireGuard do Servidor (Modo Remoto):", font=("Helvetica", 9),
                 fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"]).pack(anchor="w")
        self.entry_vpn = tk.Entry(box, bg=RED_THEME["bg_dark"], fg=RED_THEME["text_main"], font=("Helvetica", 10))
        self.entry_vpn.insert(0, self.config_data.get("vpn_ip", "10.77.0.1"))
        self.entry_vpn.pack(anchor="w", fill="x", pady=(2, 15))

        btn_save = tk.Button(box, text="💾 Salvar Configurações", bg=RED_THEME["accent_crimson"], fg="#ffffff",
                             font=("Helvetica", 9, "bold"), padx=15, pady=6, borderwidth=0, cursor="hand2",
                             command=self.save_user_config)
        btn_save.pack(anchor="w")

    def save_user_config(self):
        self.config_data["lan_ip"] = self.entry_lan.get().strip()
        self.config_data["vpn_ip"] = self.entry_vpn.get().strip()
        self.save_config()
        messagebox.showinfo("Configurações Salvas", "Endereços do alvo atualizados!")

    def create_footer(self):
        footer = tk.Frame(self, bg=RED_THEME["bg_panel"], height=30, padx=15)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.lbl_footer = tk.Label(footer, text="Wellington CyberLab — Red Team Client v2.0 | Offensive Station",
                                   font=("Helvetica", 8), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"])
        self.lbl_footer.pack(side="left")

    def telemetry_loop(self):
        while self.running:
            target = self.get_server_ip()
            api_url = f"http://{target}:8000/api/health"
            try:
                req = urllib.request.Request(api_url, headers={"User-Agent": "WellingtonRedTeam/WindowsProbe"})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    if resp.status == 200:
                        def set_online():
                            self.lbl_target_status.config(text=f"● ALVO ALCANÇÁVEL ({target}:8000)", fg=RED_THEME["accent_green"])
                        self.after(0, set_online)
            except Exception:
                def set_offline():
                    self.lbl_target_status.config(text=f"● ALVO INALCANÇÁVEL ({target})", fg=RED_THEME["accent_red"])
                self.after(0, set_offline)
            time.sleep(3)

if __name__ == "__main__":
    app = WellingtonRedTeamClientWin()
    app.mainloop()
