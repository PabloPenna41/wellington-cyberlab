#!/usr/bin/env python3
"""
Wellington Negócios — ERP Corporativo (Estilo TOTVS / Protheus Moderno)
Aplicação da Empresa fictícia rodando na LAN interna.
Contém: Tela de Autenticação / Login TOTVS, Faturamento, RH, Usuários e Portal Web.
Esta é a 'Joia da Coroa' que o Blue Team defende e o Red Team tenta invadir.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import os
import sys
import time
import threading
import urllib.request
import urllib.parse
import json
import shutil
import subprocess

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
# Paleta de Cores: CORPORATIVO / ERP (Estilo TOTVS Protheus / Fluig Moderno)
# ==============================================================================
ERP_THEME = {
    "bg_main": "#f1f5f9",         # Fundo cinza corporativo claro
    "bg_header": "#0f2744",       # Azul marinho profundo corporativo
    "bg_sidebar": "#1e3a5f",      # Azul ardósia corporativo
    "bg_card": "#ffffff",         # Fundo dos formulários e tabelas
    "border": "#cbd5e1",          # Bordas de formulário
    "text_dark": "#0f172a",       # Texto escuro nítido
    "text_muted": "#64748b",      # Texto cinza
    "accent_blue": "#0284c7",     # Acento azul institucional
    "accent_green": "#10b981",    # Aprovado / Saldo positivo
    "accent_amber": "#f59e0b",    # Pendente
    "accent_red": "#ef4444",      # Alerta / Cancelado
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "database", "wellington_erp.db")

def init_erp_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tabela de Usuários Corporativos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        cargo TEXT,
        departamento TEXT
    )
    """)

    # Tabela de Clientes e Contratos VIP
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes_vip (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT,
        cnpj TEXT,
        contrato_mensal REAL,
        status TEXT
    )
    """)

    # Tabela Financeira (Folha de Pagamento)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS folha_pagamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        funcionario TEXT,
        cargo TEXT,
        salario REAL,
        conta_bancaria TEXT
    )
    """)

    # Inserir dados padrão se vazio
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO usuarios (usuario, senha, cargo, departamento) VALUES (?, ?, ?, ?)", [
            ("admin", "AdminWellington2026!", "Diretor Executivo", "Diretoria"),
            ("contabilidade", "Contas@2026", "Analista Financeiro", "Financeiro"),
            ("rh_maria", "Maria#RH88", "Gerente de RH", "Recursos Humanos"),
            ("estagiario", "123456", "Assistente de Suporte", "TI")
        ])

        cur.executemany("INSERT INTO clientes_vip (razao_social, cnpj, contrato_mensal, status) VALUES (?, ?, ?, ?)", [
            ("Indústrias Petroquímicas Vale S.A.", "12.345.678/0001-90", 250000.00, "Ativo"),
            ("Banco de Investimentos Alpha", "98.765.432/0001-11", 580000.00, "Ativo"),
            ("Rede Varejista Brasil Forte", "55.443.221/0001-77", 125000.00, "Em Auditoria"),
            ("Logística TransGlobal Ltda", "33.221.119/0001-44", 89000.00, "Ativo")
        ])

        cur.executemany("INSERT INTO folha_pagamento (funcionario, cargo, salario, conta_bancaria) VALUES (?, ?, ?, ?)", [
            ("Wellington Silveira", "CEO & Fundador", 65000.00, "Banco 001 Ag 1234 CC 99887-1"),
            ("Carlos Drummond", "CFO Financeiro", 38000.00, "Banco 237 Ag 4321 CC 11223-4"),
            ("Mariana Costa", "Diretora de Tecnologia (CTO)", 42000.00, "Banco 341 Ag 5678 CC 33445-5"),
            ("Lucas Mendes", "Engenheiro de Redes", 14500.00, "Banco 260 Ag 0001 CC 77889-0")
        ])
        conn.commit()
    conn.close()

init_erp_database()

class WellingtonERPApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TOTVS | Wellington ERP Enterprise — Sistema Integrado de Gestão")
        self.geometry("1100x740")
        self.minsize(980, 660)
        self.configure(bg=ERP_THEME["bg_main"])

        self.current_user = None

        self.setup_header()
        self.container = tk.Frame(self, bg=ERP_THEME["bg_main"])
        self.container.pack(fill="both", expand=True)

        self.setup_footer()

        # Inicia obrigatoriamente na Tela de Login Corporativa
        self.show_login_screen()

    def setup_header(self):
        self.header = tk.Frame(self, bg=ERP_THEME["bg_header"], height=70, padx=20)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        # Logo e Título Corporativo
        left = tk.Frame(self.header, bg=ERP_THEME["bg_header"])
        left.pack(side="left", pady=12)

        lbl_logo = tk.Label(left, text="TOTVS | WELLINGTON ERP", font=("Helvetica", 14, "bold"),
                            fg="#ffffff", bg=ERP_THEME["bg_header"])
        lbl_logo.pack(anchor="w")

        lbl_sub = tk.Label(left, text="Ambiente Corporativo Interno (LAN) | Empresa Fictícia Wellington Negócios S.A.",
                           font=("Helvetica", 8), fg="#94a3b8", bg=ERP_THEME["bg_header"])
        lbl_sub.pack(anchor="w")

        # Lado Direito do Header (Status e Botões)
        self.header_right = tk.Frame(self.header, bg=ERP_THEME["bg_header"])
        self.header_right.pack(side="right", pady=14)

        btn_web = tk.Button(self.header_right, text="🌐 Acessar Site Institucional Público", bg="#0284c7", fg="#ffffff",
                            font=("Helvetica", 9, "bold"), padx=12, pady=6, borderwidth=0, cursor="hand2",
                            command=lambda: open_browser("http://127.0.0.1:8000/"))
        btn_web.pack(side="right", padx=(10, 0))

        self.lbl_user_status = tk.Label(self.header_right, text="🔒 NÃO AUTENTICADO", font=("Helvetica", 9, "bold"),
                                        fg="#f59e0b", bg=ERP_THEME["bg_header"])
        self.lbl_user_status.pack(side="right", padx=(0, 10))

    # ==========================================================================
    # TELA DE LOGIN ESTILO TOTVS
    # ==========================================================================
    def show_login_screen(self):
        for w in self.container.winfo_children():
            w.destroy()

        self.current_user = None
        self.lbl_user_status.config(text="🔒 NÃO AUTENTICADO", fg="#f59e0b")

        # Remove botão de logout se existir
        if hasattr(self, "btn_logout"):
            self.btn_logout.destroy()

        # Caixa Central de Autenticação TOTVS
        center_box = tk.Frame(self.container, bg=ERP_THEME["bg_main"])
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(center_box, bg=ERP_THEME["bg_card"], padx=40, pady=35,
                        highlightbackground=ERP_THEME["border"], highlightthickness=1)
        card.pack()

        # Logo TOTVS Card
        tk.Label(card, text="TOTVS", font=("Helvetica", 20, "bold"), fg="#0284c7", bg=ERP_THEME["bg_card"]).pack()
        tk.Label(card, text="Wellington ERP Enterprise Edition", font=("Helvetica", 11, "bold"),
                 fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_card"]).pack(pady=(2, 5))
        tk.Label(card, text="Autenticação Segura no Servidor da LAN Interna", font=("Helvetica", 9),
                 fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_card"]).pack(pady=(0, 20))

        # Campo Empresa / Filial
        tk.Label(card, text="EMPRESA / FILIAL:", font=("Helvetica", 8, "bold"),
                 fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_card"]).pack(anchor="w")
        entry_filial = tk.Entry(card, font=("Helvetica", 10), width=32, state="readonly")
        entry_filial.config(state="normal")
        entry_filial.insert(0, "01 - Wellington Negócios Matriz SP")
        entry_filial.config(state="readonly")
        entry_filial.pack(pady=(3, 12))

        # Campo Usuário
        tk.Label(card, text="USUÁRIO CORPORATIVO:", font=("Helvetica", 8, "bold"),
                 fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_card"]).pack(anchor="w")
        self.entry_login_user = tk.Entry(card, font=("Helvetica", 11), width=32)
        self.entry_login_user.pack(pady=(3, 12))
        self.entry_login_user.focus_set()

        # Campo Senha
        tk.Label(card, text="SENHA DE ACESSO:", font=("Helvetica", 8, "bold"),
                 fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_card"]).pack(anchor="w")
        self.entry_login_pass = tk.Entry(card, font=("Helvetica", 11), width=32, show="•")
        self.entry_login_pass.pack(pady=(3, 20))
        self.entry_login_pass.bind("<Return>", lambda e: self.do_login())

        # Botão Entrar
        btn_entrar = tk.Button(card, text="ENTRAR NO SISTEMA (LOGIN)", bg="#0284c7", fg="#ffffff",
                               font=("Helvetica", 10, "bold"), padx=15, pady=8, borderwidth=0, cursor="hand2",
                               command=self.do_login)
        btn_entrar.pack(fill="x", pady=(0, 15))

        # Divisor Didático
        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=10)

        # Botão de Demonstração Didática (Pegar Senha do Red Team)
        btn_fill_cracked = tk.Button(card, text="🔑 Preencher Senha Quebrada pelo Red Team",
                                     bg="#f1f5f9", fg="#b91c1c", font=("Helvetica", 8, "bold"),
                                     padx=10, pady=6, borderwidth=1, cursor="hand2",
                                     command=self.fill_from_redteam)
        btn_fill_cracked.pack(fill="x")

        self.lbl_login_msg = tk.Label(card, text="", font=("Helvetica", 9),
                                      fg=ERP_THEME["accent_red"], bg=ERP_THEME["bg_card"])
        self.lbl_login_msg.pack(pady=(10, 0))

    def do_login(self):
        usuario = self.entry_login_user.get().strip()
        senha = self.entry_login_pass.get().strip()

        if not usuario or not senha:
            self.lbl_login_msg.config(text="Por favor, preencha o usuário e a senha.", fg=ERP_THEME["accent_red"])
            return

        # Validação contra o banco de dados corporativo
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, usuario, cargo, departamento FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        row = cur.fetchone()
        conn.close()

        if row:
            self.current_user = {
                "usuario": row[1],
                "cargo": row[2],
                "departamento": row[3]
            }
            self.show_main_workspace()
        else:
            self.lbl_login_msg.config(text="Credenciais Inválidas! Usuário ou senha incorretos.", fg=ERP_THEME["accent_red"])

    def fill_from_redteam(self):
        """Consulta a API para obter a credencial que o Red Team acabou de descobrir na Força Bruta!"""
        try:
            req = urllib.request.Request("http://127.0.0.1:8000/api/erp/last-cracked")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and "usuario" in data:
                    self.entry_login_user.delete(0, tk.END)
                    self.entry_login_user.insert(0, data["usuario"])
                    self.entry_login_pass.delete(0, tk.END)
                    self.entry_login_pass.insert(0, data["senha"])
                    self.lbl_login_msg.config(
                        text=f"✓ Senha capturada na Força Bruta carregada: {data['usuario']} / {data['senha']}",
                        fg=ERP_THEME["accent_green"]
                    )
                    return
                else:
                    self.lbl_login_msg.config(
                        text="⚠️ Nenhuma senha capturada! Desative o Firewall no Blue Team e execute a Força Bruta no Red Team.",
                        fg=ERP_THEME["accent_red"]
                    )
                    return
        except Exception as e:
            self.lbl_login_msg.config(text=f"Erro ao consultar API: {e}", fg=ERP_THEME["accent_red"])

    # ==========================================================================
    # ÁREA DE TRABALHO DO SISTEMA APÓS O LOGIN
    # ==========================================================================
    def show_main_workspace(self):
        for w in self.container.winfo_children():
            w.destroy()

        u_name = self.current_user["usuario"]
        u_cargo = self.current_user["cargo"]
        self.lbl_user_status.config(text=f"👤 LOGADO: {u_name} ({u_cargo})", fg="#10b981")

        # Botão de Logout
        self.btn_logout = tk.Button(self.header_right, text="🚪 Desconectar", bg="#334155", fg="#ffffff",
                                    font=("Helvetica", 8, "bold"), padx=8, pady=4, borderwidth=0, cursor="hand2",
                                    command=self.show_login_screen)
        self.btn_logout.pack(side="right", padx=(0, 10))

        # Barra Lateral de Módulos (Estilo TOTVS)
        sidebar = tk.Frame(self.container, bg=ERP_THEME["bg_sidebar"], width=230, padx=10, pady=20)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MÓDULOS TOTVS / ERP", font=("Helvetica", 9, "bold"),
                 fg="#94a3b8", bg=ERP_THEME["bg_sidebar"]).pack(anchor="w", pady=(0, 15), padx=10)

        modules = [
            ("📊 Faturamento & Clientes", self.show_clientes),
            ("💰 Folha de Pagamento (RH)", self.show_folha),
            ("👥 Usuários & Permissões", self.show_usuarios),
            ("🌐 Portal Institucional Web", self.show_portal_web),
            ("🔒 Auditoria & Consultas", self.show_auditoria),
        ]

        for text, cmd in modules:
            btn = tk.Button(sidebar, text=text, font=("Helvetica", 9, "bold"),
                            bg=ERP_THEME["bg_sidebar"], fg="#ffffff", activebackground="#2a4d7a",
                            activeforeground="#ffffff", borderwidth=0, anchor="w", padx=12, pady=10,
                            cursor="hand2", command=cmd)
            btn.pack(fill="x", pady=2)

        # Área de Conteúdo
        self.workspace = tk.Frame(self.container, bg=ERP_THEME["bg_main"], padx=25, pady=20)
        self.workspace.pack(side="right", fill="both", expand=True)

        self.show_clientes()

    def clear_workspace(self):
        for widget in self.workspace.winfo_children():
            widget.destroy()

    def show_clientes(self):
        self.clear_workspace()
        tk.Label(self.workspace, text="MÓDULO DE FATURAMENTO: CARTEIRA DE CLIENTES VIP",
                 font=("Helvetica", 13, "bold"), fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 5))
        tk.Label(self.workspace, text="Contratos corporativos confidenciais geridos pela equipe da Wellington Negócios.",
                 font=("Helvetica", 9), fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 15))

        cols = ("ID", "Razão Social", "CNPJ", "Contrato Mensal (R$)", "Situação")
        tree = ttk.Treeview(self.workspace, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center" if col in ("ID", "Situação") else "w")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, razao_social, cnpj, contrato_mensal, status FROM clientes_vip")
        for row in cur.fetchall():
            tree.insert("", "end", values=(row[0], row[1], row[2], f"R$ {row[3]:,.2f}", row[4]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def show_folha(self):
        self.clear_workspace()
        tk.Label(self.workspace, text="MÓDULO DE RECURSOS HUMANOS: FOLHA CONFIDENCIAL",
                 font=("Helvetica", 13, "bold"), fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 5))
        tk.Label(self.workspace, text="Dados bancários e salariais da diretoria e colaboradores (Alvo crítico de auditoria).",
                 font=("Helvetica", 9), fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 15))

        cols = ("ID", "Colaborador", "Cargo", "Salário Mensal", "Conta Bancária de Depósito")
        tree = ttk.Treeview(self.workspace, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="w")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, funcionario, cargo, salario, conta_bancaria FROM folha_pagamento")
        for row in cur.fetchall():
            tree.insert("", "end", values=(row[0], row[1], row[2], f"R$ {row[3]:,.2f}", row[4]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def show_usuarios(self):
        self.clear_workspace()
        tk.Label(self.workspace, text="GESTÃO DE ACESSOS: CONTAS CORPORATIVAS DO ERP",
                 font=("Helvetica", 13, "bold"), fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 5))
        tk.Label(self.workspace, text="Contas de usuários corporativos. O Red Team tenta ataques de força bruta contra este módulo.",
                 font=("Helvetica", 9), fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 15))

        cols = ("ID", "Usuário", "Hash / Senha", "Cargo", "Departamento")
        tree = ttk.Treeview(self.workspace, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="w")

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, usuario, senha, cargo, departamento FROM usuarios")
        for row in cur.fetchall():
            tree.insert("", "end", values=(row[0], row[1], "•••••••• (Protegida)", row[3], row[4]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def show_portal_web(self):
        self.clear_workspace()
        tk.Label(self.workspace, text="PORTAL PÚBLICO INSTITUCIONAL (WELLINGTON NEGÓCIOS)",
                 font=("Helvetica", 13, "bold"), fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 5))
        tk.Label(self.workspace,
                 text="Este é o site público da empresa, hospedado no servidor do laboratório e protegido pelo Blue Team.\n"
                      "Como este computador está na rede LAN interna autorizada, seu acesso ao site NUNCA é interrompido!",
                 font=("Helvetica", 9), fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_main"], justify="left").pack(anchor="w", pady=(0, 15))

        card = tk.Frame(self.workspace, bg=ERP_THEME["bg_card"], padx=20, pady=20,
                        highlightbackground=ERP_THEME["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0, 15))

        tk.Label(card, text="STATUS DO SITE INSTITUCIONAL:", font=("Helvetica", 10, "bold"),
                 fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_card"]).pack(anchor="w", pady=(0, 8))

        lbl_status = tk.Label(card, text="● SITE ONLINE E DISPONÍVEL NA LAN (http://localhost:8000/)",
                              font=("Helvetica", 10, "bold"), fg=ERP_THEME["accent_green"], bg=ERP_THEME["bg_card"])
        lbl_status.pack(anchor="w", pady=(0, 15))

        btn_launch = tk.Button(card, text="🌐 Abrir Wellington Negócios no Navegador", bg=ERP_THEME["accent_blue"],
                               fg="#ffffff", font=("Helvetica", 10, "bold"), padx=15, pady=8,
                               borderwidth=0, cursor="hand2", command=lambda: open_browser("http://127.0.0.1:8000/"))
        btn_launch.pack(anchor="w")

    def show_auditoria(self):
        self.clear_workspace()
        tk.Label(self.workspace, text="CONSOLE DE CONSULTAS E INTEGRIDADE (SIMULADOR DE CONSULTA)",
                 font=("Helvetica", 13, "bold"), fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 5))
        tk.Label(self.workspace,
                 text="Campo de busca interna de clientes. Usado nas demonstrações de SQL Injection na Fase 4:",
                 font=("Helvetica", 9), fg=ERP_THEME["text_muted"], bg=ERP_THEME["bg_main"]).pack(anchor="w", pady=(0, 10))

        search_box = tk.Frame(self.workspace, bg=ERP_THEME["bg_main"])
        search_box.pack(fill="x", pady=(0, 10))

        tk.Label(search_box, text="Buscar Cliente por Nome: ", font=("Helvetica", 9, "bold"),
                 fg=ERP_THEME["text_dark"], bg=ERP_THEME["bg_main"]).pack(side="left")

        entry_search = tk.Entry(search_box, font=("Helvetica", 10), width=35)
        entry_search.insert(0, "Vale")
        entry_search.pack(side="left", padx=5)

        txt_result = scrolledtext.ScrolledText(self.workspace, height=12, font=("Courier", 10))
        txt_result.pack(fill="both", expand=True)

        def do_search():
            term = entry_search.get()
            txt_result.delete("1.0", tk.END)
            txt_result.insert(tk.END, f"Executando query SQL: SELECT * FROM clientes_vip WHERE razao_social LIKE '%{term}%'\n{'-'*65}\n")
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            try:
                cur.execute(f"SELECT * FROM clientes_vip WHERE razao_social LIKE '%{term}%'")
                rows = cur.fetchall()
                for r in rows:
                    txt_result.insert(tk.END, f"ID: {r[0]} | Cliente: {r[1]} | CNPJ: {r[2]} | Valor: R$ {r[3]:,.2f} | Status: {r[4]}\n")
            except Exception as e:
                txt_result.insert(tk.END, f"Erro SQL: {e}\n")
            finally:
                conn.close()

        btn_search = tk.Button(search_box, text="🔍 Consultar no ERP", bg=ERP_THEME["accent_blue"],
                               fg="#ffffff", font=("Helvetica", 9, "bold"), padx=10, pady=4,
                               borderwidth=0, cursor="hand2", command=do_search)
        btn_search.pack(side="left", padx=5)

    def setup_footer(self):
        footer = tk.Frame(self, bg=ERP_THEME["bg_header"], height=30, padx=15)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        lbl = tk.Label(footer, text="Wellington ERP Enterprise Edition (TOTVS) | Conexão Segura: LAN Interna | Protegido por Nftables & Suricata",
                       font=("Helvetica", 8), fg="#94a3b8", bg=ERP_THEME["bg_header"])
        lbl.pack(side="left")

if __name__ == "__main__":
    app = WellingtonERPApp()
    app.mainloop()
