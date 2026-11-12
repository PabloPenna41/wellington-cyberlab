#!/usr/bin/env python3
"""
Wellington CyberLab — Red Team Station (Linux CachyOS & Windows)
Interface Gráfica de Operações Ofensivas, Reconhecimento e Auditoria de Segurança
Identidade Visual: RED TEAM / Crimson Cyberpunk
Didática interativa: explica conceitos de varredura, vulnerabilidades e exploração controlada.
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
import urllib.parse
import shutil
import socket

def get_local_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

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
# Paleta de Cores: RED TEAM (Ofensivo / Carmesim / Cyberpunk)
# ==============================================================================
RED_THEME = {
    "bg_dark": "#0f0808",        # Fundo ultra escuro avermelhado
    "bg_panel": "#180d0d",       # Painel elevado
    "bg_card": "#241313",        # Cards e caixas de ferramentas
    "border": "#3d1e1e",         # Borda sutil avermelhada
    "text_main": "#fde8e8",      # Texto principal claro
    "text_muted": "#a88282",     # Texto secundário
    "accent_red": "#ef4444",     # Vermelho neon primário
    "accent_crimson": "#b91c1c",  # Carmesim escuro
    "accent_orange": "#f97316",  # Alerta / Scanning
    "accent_amber": "#f59e0b",   # Exploit / Atenção
    "accent_green": "#10b981",   # Conexão estabelecida
    "code_bg": "#120707",        # Terminal ofensivo
    "code_fg": "#fca5a5"         # Texto de código terminal
}

DEFAULT_CONFIG = {
    "lan_ip": get_local_lan_ip(),
    "vpn_ip": "10.77.0.1",
    "api_port": 8000,
    "web_port": 80,
    "active_mode": "LAN"
}

class RedTeamStation(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wellington CyberLab — Red Team Station [OFFENSIVE AUDIT]")
        self.geometry("1120x760")
        self.minsize(980, 680)
        self.configure(bg=RED_THEME["bg_dark"])

        self.config_data = DEFAULT_CONFIG.copy()
        self.target_ip = self.get_target_ip()
        self.running = True

        self.setup_styles()
        self.create_header()
        self.create_notebook()
        self.create_footer()

        # Monitor de latência e estado do firewall do alvo
        self.probe_thread = threading.Thread(target=self.target_probe_loop, daemon=True)
        self.probe_thread.start()

    def get_target_ip(self):
        preferred = self.config_data["vpn_ip"] if self.config_data["active_mode"] == "VPN" else self.config_data["lan_ip"]
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                if s.connect_ex((preferred, 8000)) == 0:
                    return preferred
        except Exception:
            pass
        return "127.0.0.1"

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

        # Esquerda: Identidade RED TEAM
        left_box = tk.Frame(header, bg=RED_THEME["bg_panel"])
        left_box.pack(side="left")

        title_row = tk.Frame(left_box, bg=RED_THEME["bg_panel"])
        title_row.pack(anchor="w")

        lbl_badge = tk.Label(title_row, text=" 🎯 RED TEAM ", font=("Helvetica", 9, "bold"),
                             fg="#ffffff", bg=RED_THEME["accent_crimson"], padx=6, pady=2)
        lbl_badge.pack(side="left", padx=(0, 10))

        lbl_title = tk.Label(title_row, text="OFFENSIVE SECURITY & AUDIT STATION",
                             font=("Helvetica", 13, "bold"), fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"])
        lbl_title.pack(side="left")

        self.lbl_target_info = tk.Label(left_box,
                                        text=f"Alvo Corporativo: {self.config_data['lan_ip']} ({self.get_target_ip()}:8000) | Escopo: Simulação Externa WAN",
                                        font=("Helvetica", 9), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"])
        self.lbl_target_info.pack(anchor="w", pady=(2, 0))

        # Direita: Seletor de Modo e Status do Alvo
        right_box = tk.Frame(header, bg=RED_THEME["bg_panel"])
        right_box.pack(side="right")

        self.btn_mode = tk.Button(right_box, text=f"Alternar p/ {'VPN' if self.config_data['active_mode'] == 'LAN' else 'LAN'}",
                                  bg=RED_THEME["bg_card"], fg=RED_THEME["accent_orange"], font=("Helvetica", 9, "bold"),
                                  padx=10, pady=5, borderwidth=1, cursor="hand2", command=self.toggle_mode)
        self.btn_mode.pack(side="right", padx=(10, 0))

        self.lbl_target_status = tk.Label(right_box, text="● SONDANDO ALVO...", font=("Helvetica", 9, "bold"),
                                          fg=RED_THEME["accent_amber"], bg=RED_THEME["bg_panel"])
        self.lbl_target_status.pack(side="right")

    def toggle_mode(self):
        new_mode = "VPN" if self.config_data["active_mode"] == "LAN" else "LAN"
        self.config_data["active_mode"] = new_mode
        self.lbl_target_info.config(text=f"Alvo Corporativo: {self.get_target_ip()}:8000 | Rota: Modo {new_mode} | Escopo: Simulação Externa")
        self.btn_mode.config(text=f"Alternar p/ {'VPN' if new_mode == 'LAN' else 'LAN'}")
        messagebox.showinfo("Alvo Redirecionado", f"Rota de teste apontada para Modo {new_mode}:\nEndpoint ativo: {self.get_target_ip()}:8000")

    def create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_fw_tests = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_recon = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_web_audit = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_tools = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_academy = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])
        self.tab_terminal = tk.Frame(self.notebook, bg=RED_THEME["bg_dark"])

        self.notebook.add(self.tab_fw_tests, text=" 💥 Testes de Ataque contra o Firewall ")
        self.notebook.add(self.tab_recon, text=" 🔍 Reconhecimento Nmap ")
        self.notebook.add(self.tab_web_audit, text=" 🌐 Auditoria Web ")
        self.notebook.add(self.tab_tools, text=" ⚔️ Ferramentas Ofensivas ")
        self.notebook.add(self.tab_academy, text=" 📚 Teoria dos Ataques ")
        self.notebook.add(self.tab_terminal, text=" 💻 Console Ofensivo ")

        self.build_fw_tests_tab()
        self.build_recon_tab()
        self.build_web_audit_tab()
        self.build_tools_tab()
        self.build_academy_tab()
        self.build_terminal_tab()

    def build_fw_tests_tab(self):
        container = tk.Frame(self.tab_fw_tests, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=15, pady=12,
                        highlightbackground=RED_THEME["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 15))

        top_title_row = tk.Frame(card, bg=RED_THEME["bg_panel"])
        top_title_row.pack(fill="x", pady=(0, 6))

        tk.Label(top_title_row, text="CENÁRIOS DE DEMONSTRAÇÃO PRÁTICA DO FIREWALL (NFTABLES)",
                 font=("Helvetica", 11, "bold"), fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(side="left")

        self.lbl_fw_live_banner = tk.Label(top_title_row, text="● Estado do Firewall no Alvo: Sincronizando...",
                                           font=("Helvetica", 9, "bold"), fg=RED_THEME["accent_amber"], bg=RED_THEME["bg_panel"])
        self.lbl_fw_live_banner.pack(side="right")

        tk.Label(card,
                 text="Execute os testes abaixo para demonstrar em tempo real como o Firewall do Blue Team reage a cada cenário:\n"
                      "• Com o Firewall ATIVO: Ataques ao ERP (Força Bruta, SQLi, Flood) são interceptados, mas o Site Público funciona (a menos que em Quarentena).\n"
                      "• Com o Firewall DESATIVADO: O Red Team consegue quebrar a senha do TOTVS na Força Bruta e extrair dados via SQL Injection!",
                 font=("Helvetica", 9), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"], justify="left").pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(card, bg=RED_THEME["bg_panel"])
        btn_row.pack(fill="x")

        # Teste 1: Teste de Acesso ao Site Principal
        btn_t1 = tk.Button(btn_row, text="1️⃣ 🌐 Testar Acesso ao Site Principal", bg=RED_THEME["accent_crimson"],
                           fg="#ffffff", font=("Helvetica", 8, "bold"), padx=10, pady=6,
                           borderwidth=0, cursor="hand2", command=self.test_website_access)
        btn_t1.pack(side="left", padx=(0, 6))

        # Teste 2: Ataque SQL Injection no ERP
        btn_sqli = tk.Button(btn_row, text="2️⃣ Injeção SQLi no ERP", bg=RED_THEME["bg_card"],
                             fg=RED_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                             borderwidth=1, cursor="hand2", command=self.test_sqli_attack)
        btn_sqli.pack(side="left", padx=(0, 6))

        # Teste 3: Ataque de Força Bruta (Brute Force Login)
        btn_brute = tk.Button(btn_row, text="3️⃣ Força Bruta no Login do TOTVS", bg="#7f1d1d",
                              fg="#ffffff", font=("Helvetica", 8, "bold"), padx=10, pady=6,
                              borderwidth=0, cursor="hand2", command=self.test_bruteforce_attack)
        btn_brute.pack(side="left", padx=(0, 6))

        # Teste 4: Flood Rate Limit
        btn_t2 = tk.Button(btn_row, text="4️⃣ Ataque Flood Anti-DoS", bg=RED_THEME["bg_card"],
                           fg=RED_THEME["accent_orange"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                           borderwidth=1, cursor="hand2", command=self.test_flood_rate_limit)
        btn_t2.pack(side="left", padx=(0, 6))

        btn_clear = tk.Button(btn_row, text="🧹 Limpar Terminal", bg=RED_THEME["bg_card"],
                              fg=RED_THEME["text_muted"], font=("Helvetica", 8), padx=8, pady=6,
                              borderwidth=1, cursor="hand2", command=lambda: self.txt_fw_test.delete("1.0", tk.END))
        btn_clear.pack(side="right")

        # Terminal de Feedback Didático
        self.txt_fw_test = scrolledtext.ScrolledText(container, bg=RED_THEME["code_bg"], fg=RED_THEME["code_fg"],
                                                    font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_fw_test.pack(fill="both", expand=True)
        self.txt_fw_test.insert(tk.END, "Selecione um cenário de teste acima para disparar contra o servidor e observar a reação do Firewall.\n")

    def test_sqli_attack(self):
        target = self.get_target_ip()
        payload = "' OR '1'='1"
        url = f"http://{target}:8000/api/erp/busca-vulneravel?client_mode=redteam&q=" + urllib.parse.quote(payload)
        self.txt_fw_test.insert(tk.END, f"\n[TESTE 2: SQL INJECTION] Alvo: Wellington ERP | Payload: {payload}\nURL: {url}\n{'-'*75}\n")
        self.txt_fw_test.see(tk.END)

        def task():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "SQLi-Exploiter/1.0"})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    self.txt_fw_test.insert(tk.END, f"[🔓 VULNERABILIDADE EXPLORADA COM SUCESSO!]\n")
                    self.txt_fw_test.insert(tk.END, f"    Query Executada no Servidor: {data.get('query_executed')}\n")
                    self.txt_fw_test.insert(tk.END, f"    CONTRATOS CONFIDENCIAIS VAZADOS DOS CLIENTES VIP:\n")
                    for row in data.get("results", []):
                        self.txt_fw_test.insert(tk.END, f"    -> ID {row[0]}: {row[1]} | CNPJ: {row[2]} | R$ {row[3]:,.2f}\n")
                    self.txt_fw_test.insert(tk.END,
                        f"\n[DIDÁTICA DO ATAQUE]:\n"
                        f"• Como o Firewall estava DESATIVADO (ou sem regras experimentais), o payload SQLi chegou ao banco!\n"
                        f"• A condição OR '1'='1' retornou todos os registros confidenciais da empresa.\n"
                        f"• Vá no Blue Team e clique em '🟢 ATIVAR / RESTAURAR FIREWALL' para bloquear este ataque!\n\n")
                    self.txt_fw_test.see(tk.END)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="ignore")
                self.txt_fw_test.insert(tk.END,
                    f"[🛡️ ATAQUE SQLi BLOQUEADO PELO FIREWALL! (HTTP {e.code})]\n"
                    f"   -> Resposta da Defesa: {err_body}\n"
                    f"   -> PARA DEMONSTRAR O VAZAMENTO DE DADOS:\n"
                    f"      Vá no Blue Team e clique em '🔴 DESATIVAR FIREWALL COMPLETAMENTE', depois clique neste botão novamente!\n\n")
                self.txt_fw_test.see(tk.END)
            except Exception as e:
                self.txt_fw_test.insert(tk.END, f"[X] Erro de conexão com o backend ({target}:8000): {e}\n\n")
                self.txt_fw_test.see(tk.END)
        threading.Thread(target=task, daemon=True).start()

    def test_bruteforce_attack(self):
        target = self.get_target_ip()
        url = f"http://{target}:8000/api/erp/login"
        self.txt_fw_test.insert(tk.END, f"\n[TESTE 3: FORÇA BRUTA NO LOGIN DO TOTVS] Alvo: ({url})\n")
        self.txt_fw_test.insert(tk.END, "Testando dicionário de senhas contra a conta corporativa 'admin'...\n" + ("-" * 75) + "\n")
        self.txt_fw_test.see(tk.END)

        passwords = ["123456", "admin", "password", "wellington", "Admin2026", "AdminWellington2026!"]
        def task():
            cracked = False
            blocked = False
            for pwd in passwords:
                payload = json.dumps({
                    "usuario": "admin",
                    "senha": pwd,
                    "client_mode": "redteam"
                }).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json", "User-Agent": "BruteForceBot/2.0"}
                )
                try:
                    with urllib.request.urlopen(req, timeout=2.0) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        if res.get("success"):
                            self.txt_fw_test.insert(tk.END, f"  [✓ SENHA QUEBRADA!] Usuário: admin | Senha: {pwd} | Cargo: {res.get('cargo')}\n")
                            cracked = True
                            break
                        else:
                            self.txt_fw_test.insert(tk.END, f"  [FALHA] Testando 'admin' com senha '{pwd}': Credencial incorreta\n")
                except urllib.error.HTTPError as e:
                    if e.code in (403, 429):
                        blocked = True
                        self.txt_fw_test.insert(tk.END, f"  [🛡️ FIREWALL DROP {e.code}] Tentativa com '{pwd}' interceptada e descartada pelo Firewall!\n")
                    else:
                        self.txt_fw_test.insert(tk.END, f"  [ERRO HTTP {e.code}] Tentativa com '{pwd}': {e.reason}\n")
                except Exception as e:
                    self.txt_fw_test.insert(tk.END, f"  [X ERRO DE REDE] Falha ao contatar {url}: {e}\n")
                self.txt_fw_test.see(tk.END)
                time.sleep(0.12)

            if cracked:
                self.txt_fw_test.insert(tk.END,
                    f"\n"
                    f"╔═══════════════════════════════════════════════════════════════════════════════════╗\n"
                    f"║ 🔓 CREDENCIAIS CAPTURADAS COM SUCESSO (WELLINGTON ERP / TOTVS)                    ║\n"
                    f"╠═══════════════════════════════════════════════════════════════════════════════════╣\n"
                    f"║  Usuário Alvo: admin                                                             ║\n"
                    f"║  Senha Obtida: AdminWellington2026!                                              ║\n"
                    f"║  Privilégio:   Diretor Executivo (Acesso Total / Confidencial)                   ║\n"
                    f"╚═══════════════════════════════════════════════════════════════════════════════════╝\n\n"
                    f"👉 PASSO A PASSO DIDÁTICO PARA A DEMONSTRAÇÃO:\n"
                    f"   1. Vá na janela 'TOTVS | Wellington ERP Enterprise'.\n"
                    f"   2. Na tela de login, clique em: '🔑 Preencher Senha Quebrada pelo Red Team'.\n"
                    f"   3. Clique em 'ENTRAR NO SISTEMA (LOGIN)' para acessar os dados confidenciais!\n\n"
                )
            elif blocked:
                self.txt_fw_test.insert(tk.END,
                    f"\n"
                    f"[🛡️ ATAQUE BARRADO PELO FIREWALL DO BLUE TEAM]\n"
                    f"O Firewall Nftables ativo interceptou as tentativas de força bruta!\n\n"
                    f"👉 PARA DEMONSTRAR A QUEBRA DE SENHA:\n"
                    f"   1. Vá na janela do Blue Team (Central de Defesa).\n"
                    f"   2. Clique no botão vermelho: '🔴 DESATIVAR FIREWALL COMPLETAMENTE (Modo Aberto)'.\n"
                    f"   3. Volte aqui e clique novamente em '3️⃣ Força Bruta no Login do TOTVS'.\n"
                    f"   4. Com o firewall desligado, o ataque descobrirá a senha 'AdminWellington2026!'!\n\n"
                )
            else:
                self.txt_fw_test.insert(tk.END, f"\n[-] Ataque finalizado.\n\n")
            self.txt_fw_test.see(tk.END)
        threading.Thread(target=task, daemon=True).start()

    def test_website_access(self):
        target = self.get_target_ip()
        url = f"http://{target}:8000/?client_mode=redteam"
        self.txt_fw_test.insert(tk.END, f"\n[TESTE 1: ACESSO AO SITE PRINCIPAL] Conectando em {url}...\n")
        self.txt_fw_test.see(tk.END)

        def task():
            start_t = time.time()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "RedTeamExternalBrowser/1.0"})
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    elapsed = round((time.time() - start_t) * 1000, 1)
                    self.txt_fw_test.insert(tk.END,
                        f"[✓ HTTP 200 OK — SITE LIBERADO EM {elapsed}ms!]\n"
                        f"   -> O Red Team conseguiu acessar o portal institucional da Wellington Negócios!\n"
                        f"   -> Abrindo página no navegador...\n"
                        f"   -> DICA: Para bloquear este acesso, vá no Blue Team e clique em '🚫 BLOQUEAR SITE PARA O RED TEAM'!\n\n")
                    self.txt_fw_test.see(tk.END)
                    open_browser(f"http://{target}:8000/?client_mode=redteam")
            except urllib.error.HTTPError as e:
                elapsed = round((time.time() - start_t) * 1000, 1)
                err_msg = e.read().decode("utf-8", errors="ignore")
                self.txt_fw_test.insert(tk.END,
                    f"\n[🚫 ACESSO BLOQUEADO PELO BLUE TEAM! (HTTP {e.code} em {elapsed}ms)]\n"
                    f"   -> Resposta do Firewall: {err_msg}\n"
                    f"   -> O Blue Team colocou o Red Team em Quarentena! O site está inacessível para você.\n"
                    f"   -> DICA: Vá no Blue Team e clique em '✅ LIBERAR SITE PARA O RED TEAM' para restaurar o acesso!\n\n")
                self.txt_fw_test.see(tk.END)
                messagebox.showerror(
                    "Acesso Bloqueado pelo Firewall (403 DROP)",
                    "🚫 BLOQUEADO PELO BLUE TEAM!\n\n"
                    "O seu IP está na Quarentena do Firewall Nftables.\n"
                    "Para liberar o site, clique em '✅ LIBERAR SITE PARA O RED TEAM' na janela do Blue Team."
                )
            except Exception as e:
                self.txt_fw_test.insert(tk.END, f"\n[X ERRO DE CONEXÃO]: Não foi possível conectar em {url}: {e}\n\n")
                self.txt_fw_test.see(tk.END)
        threading.Thread(target=task, daemon=True).start()

    def test_flood_rate_limit(self):
        target = self.get_target_ip()
        self.txt_fw_test.insert(tk.END, f"\n[TESTE 4: FLOOD ANTI-DoS] Disparando rajada de 20 requisições para http://{target}:8000/api/health...\n")
        self.txt_fw_test.see(tk.END)

        def task():
            success_count = 0
            blocked_count = 0
            for i in range(1, 21):
                url = f"http://{target}:8000/api/health?client_mode=redteam&flood_seq={i}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": f"FloodTester/{i}"})
                    with urllib.request.urlopen(req, timeout=1.5) as resp:
                        success_count += 1
                        self.txt_fw_test.insert(tk.END, f"  [REQ #{i:02d}] 200 OK — Aceita pelo Servidor\n")
                except urllib.error.HTTPError as e:
                    blocked_count += 1
                    reason = "Quarentena Ativa" if e.code == 403 else "Rate-Limit Anti-DoS (meter http_flood)"
                    self.txt_fw_test.insert(tk.END, f"  [REQ #{i:02d}] 🛡️ BLOQUEADA (HTTP {e.code}) — Cortada por: {reason}!\n")
                except Exception as e:
                    blocked_count += 1
                    self.txt_fw_test.insert(tk.END, f"  [REQ #{i:02d}] Erro: {e}\n")
                self.txt_fw_test.see(tk.END)
                time.sleep(0.04)

            self.txt_fw_test.insert(tk.END,
                f"\n--- RESULTADO DO TESTE DE FLOOD (ANTI-DoS) ---\n"
                f"Requisições Aceitas: {success_count} | Bloqueadas pelo Firewall: {blocked_count}\n\n")
            self.txt_fw_test.see(tk.END)
        threading.Thread(target=task, daemon=True).start()

    def test_drop_vs_reject(self):
        target = self.get_target_ip()
        self.txt_fw_test.insert(tk.END, f"\n[TESTE 3] Comparando comportamento: DROP vs REJECT contra {target}...\n")
        self.txt_fw_test.see(tk.END)

        def task():
            # 1. Porta 8080 (REJECT com TCP Reset no Nftables)
            self.txt_fw_test.insert(tk.END, "[*] Testando Porta 8080 (Regra Experimental: REJECT com TCP Reset)...\n")
            s_time = time.time()
            try:
                subprocess.run(f"nc -z -v -w 2 {target} 8080", shell=True, capture_output=True, text=True)
            except Exception:
                pass
            diff1 = round((time.time() - s_time) * 1000, 1)
            self.txt_fw_test.insert(tk.END,
                f"   -> Resposta imediata em {diff1}ms (Conexão Recusada / RST).\n"
                f"   -> DIDÁTICA: O servidor avisa o atacante imediatamente que a porta está fechada.\n\n")

            # 2. Porta 9999 (DROP silencioso da Política Padrão)
            self.txt_fw_test.insert(tk.END, "[*] Testando Porta 9999 (Política Padrão do Firewall: DROP silencioso)...\n")
            s_time = time.time()
            try:
                subprocess.run(f"nc -z -v -w 2 {target} 9999", shell=True, capture_output=True, text=True)
            except Exception:
                pass
            diff2 = round((time.time() - s_time) * 1000, 1)
            self.txt_fw_test.insert(tk.END,
                f"   -> Demorou {diff2}ms (Timeout total).\n"
                f"   -> DIDÁTICA: O firewall ignora o pacote. O atacante perde tempo esperando resposta!\n\n")
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # ABA 1: RECONHECIMENTO (PORTAS / NMAP)
    # ==========================================================================
    def build_recon_tab(self):
        container = tk.Frame(self.tab_recon, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Painel de Controle de Varreduras
        ctrl_card = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=15, pady=12,
                             highlightbackground=RED_THEME["border"], highlightthickness=1)
        ctrl_card.pack(fill="x", pady=(0, 15))

        tk.Label(ctrl_card, text="MÓDULO DE RECONHECIMENTO ATIVO (NMAP SCANNER)", font=("Helvetica", 11, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 6))

        tk.Label(ctrl_card,
                 text="Selecione um perfil de varredura pré-configurado contra a máquina alvo para analisar como o Nftables e o Suricata reagem:",
                 font=("Helvetica", 9), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(ctrl_card, bg=RED_THEME["bg_panel"])
        btn_row.pack(fill="x")

        # Botão 1: Scan Rápido do Lab
        btn_fast = tk.Button(btn_row, text="⚡ Scan Lab (80, 443, 8000, 51820)", bg=RED_THEME["bg_card"],
                             fg=RED_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                             borderwidth=1, cursor="hand2", command=lambda: self.execute_scan("-p 80,443,8000,51820 -T4"))
        btn_fast.pack(side="left", padx=(0, 8))

        # Botão 2: Detecção de Serviços
        btn_svc = tk.Button(btn_row, text="🔬 Versões & Banners (-sV -sC)", bg=RED_THEME["bg_card"],
                            fg=RED_THEME["accent_orange"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                            borderwidth=1, cursor="hand2", command=lambda: self.execute_scan("-sV -sC -p 80,8000"))
        btn_svc.pack(side="left", padx=(0, 8))

        # Botão 3: Scan TCP Completo
        btn_syn = tk.Button(btn_row, text="🥷 Scan TCP Connect (-sT)", bg=RED_THEME["bg_card"],
                            fg=RED_THEME["accent_amber"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                            borderwidth=1, cursor="hand2", command=lambda: self.execute_scan("-sT -p 22,80,443,8000,8080"))
        btn_syn.pack(side="left", padx=(0, 8))

        # Botão 4: Scan Rápido Top Portas
        btn_udp = tk.Button(btn_row, text="📡 Scan Top Portas (--top-ports 20)", bg=RED_THEME["bg_card"],
                            fg=RED_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                            borderwidth=1, cursor="hand2", command=lambda: self.execute_scan("--top-ports 20 -T4"))
        btn_udp.pack(side="left")

        # Saída do Terminal com explicação em tempo real
        self.txt_recon = scrolledtext.ScrolledText(container, bg=RED_THEME["code_bg"], fg=RED_THEME["code_fg"],
                                                  font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_recon.pack(fill="both", expand=True)
        self.txt_recon.insert(tk.END, "=== TERMINAL DE RECONHECIMENTO RED TEAM ===\nPronto para iniciar o reconhecimento do alvo do laboratório.\n")

    def execute_scan(self, flags):
        target = self.get_target_ip()
        self.txt_recon.insert(tk.END, f"\n[!] INICIANDO VARREDURA DE PORTAS:\n    Comando: nmap {flags} {target}\n"
                                      f"    Objetivo: Identificar portas abertas e serviços ativos no servidor.\n"
                                      f"{'-'*75}\n")
        self.txt_recon.see(tk.END)

        def task():
            # Verificar estado do Firewall no Alvo antes do scan
            try:
                with urllib.request.urlopen(f"http://{target}:8000/api/firewall/state", timeout=1.5) as r:
                    st = json.loads(r.read().decode("utf-8"))
                    if st.get("firewall_enabled") and st.get("quarantine_active"):
                        self.txt_recon.insert(tk.END,
                            "[🚫 BLOQUEADO PELA QUARENTENA DO NFTABLES]\n"
                            "O IP do Red Team encontra-se bloqueado na regra '@redteam_blacklist'.\n"
                            "Todos os pacotes de sondagem foram descartados (DROP) pelo Firewall do Blue Team!\n")
                        self.txt_recon.see(tk.END)
                        return
            except Exception:
                pass

            cmd = f"nmap {flags} {target}"
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.txt_recon.insert(tk.END, line)
                    self.txt_recon.see(tk.END)
                proc.wait()
                self.txt_recon.insert(tk.END, f"\n[✓] Reconhecimento concluído com sucesso!\n")
                self.txt_recon.see(tk.END)
            except Exception as e:
                self.txt_recon.insert(tk.END, f"\n[X] Falha na execução: {e}\n")
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # ABA 2: AUDITORIA WEB (WELLINGTON NEGÓCIOS)
    # ==========================================================================
    def build_web_audit_tab(self):
        container = tk.Frame(self.tab_web_audit, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        card = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=15, pady=12,
                        highlightbackground=RED_THEME["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="ALVOS WEB DO LABORATÓRIO (WELLINGTON NEGÓCIOS)", font=("Helvetica", 11, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 6))

        tk.Label(card,
                 text="Inspecione os cabeçalhos HTTP ou teste a abertura do site público sob as regras atuais do Firewall:",
                 font=("Helvetica", 9), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"]).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(card, bg=RED_THEME["bg_panel"])
        grid.pack(fill="x")

        # Botão: Inspecionar Headers HTTP
        btn_headers = tk.Button(grid, text="🔎 Auditar Cabeçalhos de Segurança (HTTP Headers)", bg=RED_THEME["bg_card"],
                                fg=RED_THEME["text_main"], font=("Helvetica", 8, "bold"), padx=10, pady=6,
                                borderwidth=1, cursor="hand2", command=self.audit_security_headers)
        btn_headers.pack(side="left", padx=(0, 10))

        # Botão: Abrir no Navegador Externo (respeitando bloqueio do Firewall)
        btn_browser = tk.Button(grid, text="🌐 Testar e Abrir Site Alvo no Navegador", bg=RED_THEME["accent_crimson"],
                                fg="#ffffff", font=("Helvetica", 8, "bold"), padx=10, pady=6,
                                borderwidth=0, cursor="hand2",
                                command=self.test_website_access)
        btn_browser.pack(side="left")

        # Terminal de Auditoria Web
        self.txt_web = scrolledtext.ScrolledText(container, bg=RED_THEME["code_bg"], fg=RED_THEME["code_fg"],
                                                font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_web.pack(fill="both", expand=True)
        self.txt_web.insert(tk.END, "Selecione uma ação para auditar as respostas HTTP do servidor.\n")

    def audit_security_headers(self):
        target = self.get_target_ip()
        url = f"http://{target}:8000/?client_mode=redteam"
        self.txt_web.insert(tk.END, f"\n[+] Enviando requisição GET para inspeção de segurança: {url}\n{'-'*75}\n")

        def task():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "WellingtonRedTeam-Scanner/1.0"})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    headers = resp.info()
                    self.txt_web.insert(tk.END, f"Status HTTP: {resp.status} {resp.reason}\n\n")
                    self.txt_web.insert(tk.END, "=== ANÁLISE DIDÁTICA DE CABEÇALHOS DEFENSIVOS ===\n")

                    checks = [
                        ("X-Frame-Options", "Proteção contra Clickjacking (iframes não autorizados)"),
                        ("X-Content-Type-Options", "Prevenção contra MIME-sniffing de scripts"),
                        ("X-XSS-Protection", "Filtro preliminar de scripts maliciosos refletidos"),
                        ("Referrer-Policy", "Controle de vazamento de URLs e metadados"),
                        ("Content-Security-Policy", "Política estrita de execução de scripts (CSP)")
                    ]

                    for h_name, desc in checks:
                        val = headers.get(h_name)
                        if val:
                            self.txt_web.insert(tk.END, f"[✓ PRESENTE] {h_name}: {val}\n    -> {desc}\n")
                        else:
                            self.txt_web.insert(tk.END, f"[! AUSENTE ] {h_name}: Não configurado na resposta da API!\n    -> Recomendação defensiva: {desc}\n")

                    self.txt_web.insert(tk.END, f"\nTodos os cabeçalhos recebidos:\n{headers}\n")
            except urllib.error.HTTPError as e:
                self.txt_web.insert(tk.END, f"[🚫 BLOQUEADO PELO FIREWALL - HTTP {e.code}]: O Blue Team bloqueou o acesso do Red Team ao site!\n")
            except Exception as e:
                self.txt_web.insert(tk.END, f"[X] Falha ao conectar em {url}: {e}\n")
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # ABA 3: FERRAMENTAS OFENSIVAS
    # ==========================================================================
    def build_tools_tab(self):
        container = tk.Frame(self.tab_tools, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="SUÍTE DE FERRAMENTAS DE TESTE DE INVASÃO", font=("Helvetica", 12, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_dark"]).pack(anchor="w", pady=(0, 10))

        tools_data = [
            ("Burp Suite Community", "Proxy interceptador HTTP/HTTPS para auditoria de requisições, injeção de parâmetros e testes manuais.", "burpsuite"),
            ("Wireshark", "Analisador de pacotes de rede para dissecar tráfego pcap e verificar se dados transitam em texto claro.", "wireshark"),
            ("Curl Engine", "Cliente HTTP para forjar requisições customizadas, verbos inseguros e payloads HTTP.", "curl"),
            ("Nmap Network Mapper", "Mapeamento ativo de topologia, detecção de SO e fingerprint de serviços abertos.", "nmap")
        ]

        for title, desc, bin_cmd in tools_data:
            card = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=15, pady=12,
                            highlightbackground=RED_THEME["border"], highlightthickness=1)
            card.pack(fill="x", pady=5)

            info = tk.Frame(card, bg=RED_THEME["bg_panel"])
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=title, font=("Helvetica", 10, "bold"), fg=RED_THEME["text_main"],
                     bg=RED_THEME["bg_panel"]).pack(anchor="w")
            tk.Label(info, text=desc, font=("Helvetica", 8), fg=RED_THEME["text_muted"],
                     bg=RED_THEME["bg_panel"]).pack(anchor="w")

            btn_launch = tk.Button(card, text=f"Lançar {bin_cmd}", bg=RED_THEME["bg_card"],
                                   fg=RED_THEME["accent_orange"], font=("Helvetica", 8, "bold"),
                                   padx=10, pady=5, borderwidth=1, cursor="hand2",
                                   command=lambda b=bin_cmd: self.launch_external_tool(b))
            btn_launch.pack(side="right")

    def launch_external_tool(self, cmd):
        try:
            subprocess.Popen([cmd])
        except Exception:
            messagebox.showinfo("Ferramenta Externa", f"A ferramenta '{cmd}' pode ser iniciada se estiver instalada no PATH do sistema.")

    # ==========================================================================
    # ABA 4: DIDÁTICA E TEORIA DOS ATAQUES
    # ==========================================================================
    def build_academy_tab(self):
        container = tk.Frame(self.tab_academy, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        txt_academy = scrolledtext.ScrolledText(container, bg=RED_THEME["bg_panel"], fg=RED_THEME["text_main"],
                                                font=("Helvetica", 10), borderwidth=0, padx=15, pady=15)
        txt_academy.pack(fill="both", expand=True)

        content = """
================================================================================
          WELLINGTON CYBERLAB — CADERNO DIDÁTICO DE ENGENHARIA E CIBERSEGURANÇA
================================================================================

🎯 O PAPEL DO RED TEAM:
O Red Team tem como responsabilidade simular táticas, técnicas e procedimentos (TTPs)
adotados por agentes maliciosos no mundo real. Nosso objetivo no laboratório NÃO é
destruir o ambiente, mas sim validar a resiliência das defesas (Blue Team).

--------------------------------------------------------------------------------
1. COMO FUNCIONA O RECONHECIMENTO (PORT SCANNING):
--------------------------------------------------------------------------------
- Varredura TCP Connect (-sT): Completa o handshake de 3 vias para verificar portas abertas.
- Detecção de Serviços (-sV): O scanner estabelece a conexão e envia requisições
  de teste (probes), lendo o banner retornado para identificar o serviço.

--------------------------------------------------------------------------------
2. CENÁRIOS PRÁTICOS DE DEMONSTRAÇÃO DO FIREWALL:
--------------------------------------------------------------------------------
- Quarentena Ativa (Bloquear Site): O IP do Red Team é bloqueado inclusive no site público.
- Firewall Ativo (Modo Blindado): O site público fica acessível, mas ataques ao ERP
  (Força Bruta, SQL Injection e Flood DoS) são bloqueados!
- Firewall Desativado (Modo Aberto): Todos os ataques passam livremente, permitindo
  quebrar a senha do TOTVS e extrair o banco de dados via SQL Injection!
================================================================================
"""
        txt_academy.insert(tk.END, content)
        txt_academy.config(state="disabled")

    # ==========================================================================
    # ABA 5: CONSOLE OFENSIVO INTERATIVO
    # ==========================================================================
    def build_terminal_tab(self):
        container = tk.Frame(self.tab_terminal, bg=RED_THEME["bg_dark"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        entry_bar = tk.Frame(container, bg=RED_THEME["bg_panel"], padx=10, pady=8)
        entry_bar.pack(fill="x", pady=(0, 10))

        tk.Label(entry_bar, text="COMANDO: ", font=("Helvetica", 9, "bold"),
                 fg=RED_THEME["accent_red"], bg=RED_THEME["bg_panel"]).pack(side="left")

        self.entry_cmd = tk.Entry(entry_bar, bg=RED_THEME["bg_dark"], fg=RED_THEME["text_main"],
                                  font=("Courier", 10), insertbackground=RED_THEME["accent_red"])
        self.entry_cmd.pack(side="left", fill="x", expand=True, padx=8)
        self.entry_cmd.insert(0, f"curl -I http://{self.get_target_ip()}:8000/")
        self.entry_cmd.bind("<Return>", lambda e: self.run_custom_cmd())

        btn_run = tk.Button(entry_bar, text="Executar", bg=RED_THEME["accent_crimson"], fg="#ffffff",
                            font=("Helvetica", 8, "bold"), padx=12, pady=4, borderwidth=0, cursor="hand2",
                            command=self.run_custom_cmd)
        btn_run.pack(side="right")

        self.txt_term = scrolledtext.ScrolledText(container, bg=RED_THEME["code_bg"], fg=RED_THEME["code_fg"],
                                                 font=("Courier", 10), borderwidth=0, padx=12, pady=12)
        self.txt_term.pack(fill="both", expand=True)

    def run_custom_cmd(self):
        cmd = self.entry_cmd.get().strip()
        if not cmd:
            return
        self.txt_term.insert(tk.END, f"\n$ {cmd}\n")
        self.txt_term.see(tk.END)

        def task():
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.txt_term.insert(tk.END, line)
                    self.txt_term.see(tk.END)
                proc.wait()
            except Exception as e:
                self.txt_term.insert(tk.END, f"Erro: {e}\n")
        threading.Thread(target=task, daemon=True).start()

    # ==========================================================================
    # PROBE LOOP E FOOTER (SINCRONIZAÇÃO EM TEMPO REAL COM O BLUE TEAM)
    # ==========================================================================
    def create_footer(self):
        footer = tk.Frame(self, bg=RED_THEME["bg_panel"], height=30, padx=15)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.lbl_footer = tk.Label(footer, text="Wellington CyberLab — Red Team Station v2.0 | Conectado ao Motor de Simulação",
                                   font=("Helvetica", 8), fg=RED_THEME["text_muted"], bg=RED_THEME["bg_panel"])
        self.lbl_footer.pack(side="left")

    def target_probe_loop(self):
        while self.running:
            target = self.get_target_ip()
            state_url = f"http://{target}:8000/api/firewall/state"
            try:
                req = urllib.request.Request(state_url, headers={"User-Agent": "WellingtonRedTeam/Probe"})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        fw_on = data.get("firewall_enabled", True)
                        exp_on = data.get("experimental_enabled", True)
                        quar_on = data.get("quarantine_active", False)

                        def update_status():
                            if not fw_on:
                                self.lbl_target_status.config(
                                    text=f"● ALVO VULNERÁVEL: FIREWALL DESATIVADO ({target}:8000)",
                                    fg=RED_THEME["accent_green"]
                                )
                                self.lbl_fw_live_banner.config(
                                    text="🔓 FIREWALL DO ALVO: DESATIVADO (Modo Aberto — Todos os ataques liberados!)",
                                    fg=RED_THEME["accent_green"]
                                )
                            elif quar_on:
                                self.lbl_target_status.config(
                                    text=f"● BLOQUEADO EM QUARENTENA PELO BLUE TEAM ({target}:8000)",
                                    fg=RED_THEME["accent_red"]
                                )
                                self.lbl_fw_live_banner.config(
                                    text="🚫 FIREWALL DO ALVO: QUARENTENA ATIVA (Site e ERP bloqueados para o Red Team)",
                                    fg=RED_THEME["accent_red"]
                                )
                            elif exp_on:
                                self.lbl_target_status.config(
                                    text=f"● ALVO PROTEGIDO POR FIREWALL ({target}:8000)",
                                    fg=RED_THEME["accent_amber"]
                                )
                                self.lbl_fw_live_banner.config(
                                    text="🛡️ FIREWALL DO ALVO: ATIVO (Site Público: LIBERADO | Ataques ERP: BLOQUEADOS)",
                                    fg=RED_THEME["accent_amber"]
                                )
                            else:
                                self.lbl_target_status.config(
                                    text=f"● ALVO EM MODO BÁSICO ({target}:8000)",
                                    fg=RED_THEME["accent_orange"]
                                )
                                self.lbl_fw_live_banner.config(
                                    text="⚠️ FIREWALL DO ALVO: SÓ PERMANENTES (Regras Experimentais Desligadas)",
                                    fg=RED_THEME["accent_orange"]
                                )
                        self.after(0, update_status)
            except Exception:
                def set_offline():
                    self.lbl_target_status.config(text=f"● SERVIDOR OFFLINE ({target}:8000)", fg=RED_THEME["accent_red"])
                self.after(0, set_offline)
            time.sleep(1.5)

if __name__ == "__main__":
    app = RedTeamStation()
    app.mainloop()
