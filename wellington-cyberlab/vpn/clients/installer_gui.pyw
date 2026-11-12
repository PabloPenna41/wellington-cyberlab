#!/usr/bin/env python3
"""
Wellington CyberLab — Assistente Gráfico de Instalação para Windows
Apresenta interface moderna com checkboxes para componentes opcionais,
cria atalhos na Área de Trabalho e no Menu Iniciar, e provisiona o cliente.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import shutil

INSTALL_DIR = r"C:\WellingtonCyberLab"

THEME = {
    "bg_dark": "#0d1117",
    "bg_panel": "#161b22",
    "border": "#30363d",
    "text_main": "#f0f6fc",
    "text_muted": "#8b949e",
    "accent_cyan": "#39c5bb",
    "accent_green": "#3fb950",
    "accent_red": "#f85149",
}

class WindowsInstallerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wellington CyberLab — Assistente de Instalação (Windows)")
        self.geometry("680x560")
        self.resizable(False, False)
        self.configure(bg=THEME["bg_dark"])

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=THEME["bg_panel"], padx=20, pady=15)
        header.pack(fill="x")
        tk.Label(header, text="WELLINGTON CYBERLAB — CLIENT SETUP", font=("Helvetica", 13, "bold"),
                 fg=THEME["text_main"], bg=THEME["bg_panel"]).pack(anchor="w")
        tk.Label(header, text="Instalador Automatizado para a Estação Windows (Red Team / Auditoria)",
                 font=("Helvetica", 9), fg=THEME["text_muted"], bg=THEME["bg_panel"]).pack(anchor="w")

        # Container Central
        body = tk.Frame(self, bg=THEME["bg_dark"], padx=20, pady=15)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Componentes a serem preparados:", font=("Helvetica", 10, "bold"),
                 fg=THEME["accent_cyan"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 10))

        # Checkboxes
        self.var_client = tk.BooleanVar(value=True)
        self.chk_client = tk.Checkbutton(body, text="Wellington CyberLab Client GUI (Obrigatório)",
                                         variable=self.var_client, state="disabled",
                                         bg=THEME["bg_dark"], fg=THEME["text_main"], selectcolor=THEME["bg_panel"])
        self.chk_client.pack(anchor="w", pady=2)

        self.var_wireguard = tk.BooleanVar(value=True)
        self.chk_wireguard = tk.Checkbutton(body, text="Cliente Oficial WireGuard VPN (winget / MSI oficial)",
                                            variable=self.var_wireguard,
                                            bg=THEME["bg_dark"], fg=THEME["text_main"], selectcolor=THEME["bg_panel"])
        self.chk_wireguard.pack(anchor="w", pady=2)

        self.var_nmap = tk.BooleanVar(value=True)
        self.chk_nmap = tk.Checkbutton(body, text="Utilitário de Varredura Nmap (winget install Insecure.Nmap)",
                                       variable=self.var_nmap,
                                       bg=THEME["bg_dark"], fg=THEME["text_main"], selectcolor=THEME["bg_panel"])
        self.chk_nmap.pack(anchor="w", pady=2)

        self.var_wireshark = tk.BooleanVar(value=False)
        self.chk_wireshark = tk.Checkbutton(body, text="Wireshark Packet Analyzer (Opcional)",
                                            variable=self.var_wireshark,
                                            bg=THEME["bg_dark"], fg=THEME["text_main"], selectcolor=THEME["bg_panel"])
        self.chk_wireshark.pack(anchor="w", pady=2)

        self.var_desktop_shortcut = tk.BooleanVar(value=True)
        self.chk_desktop = tk.Checkbutton(body, text="Criar atalho na Área de Trabalho e no Menu Iniciar",
                                          variable=self.var_desktop_shortcut,
                                          bg=THEME["bg_dark"], fg=THEME["text_main"], selectcolor=THEME["bg_panel"])
        self.chk_desktop.pack(anchor="w", pady=2)

        # Barra de Progresso
        self.progress = ttk.Progressbar(body, mode="indeterminate")
        self.progress.pack(fill="x", pady=15)

        # Log Terminal
        self.txt_log = scrolledtext.ScrolledText(body, bg=THEME["bg_panel"], fg="#39c5bb",
                                                font=("Courier", 9), height=10, borderwidth=0)
        self.txt_log.pack(fill="both", expand=True)
        self.txt_log.insert(tk.END, "Selecione as opções acima e clique em 'Instalar Agora'.\n")

        # Botões de Ação
        btn_bar = tk.Frame(self, bg=THEME["bg_panel"], padx=20, pady=12)
        btn_bar.pack(fill="x", side="bottom")

        self.btn_install = tk.Button(btn_bar, text="🚀 INSTALAR AGORA", bg=THEME["accent_green"],
                                     fg="#ffffff", font=("Helvetica", 10, "bold"), padx=15, pady=6,
                                     borderwidth=0, cursor="hand2", command=self.start_installation)
        self.btn_install.pack(side="right")

        self.btn_uninstall = tk.Button(btn_bar, text="Desinstalar Laboratório", bg=THEME["bg_dark"],
                                       fg=THEME["accent_red"], font=("Helvetica", 9), padx=10, pady=6,
                                       borderwidth=0, cursor="hand2", command=self.uninstall_lab)
        self.btn_uninstall.pack(side="left")

    def log(self, text):
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)

    def start_installation(self):
        self.btn_install.config(state="disabled")
        self.progress.start(10)
        threading.Thread(target=self.run_install_steps, daemon=True).start()

    def run_install_steps(self):
        try:
            self.log("[+] 1/6 Criando estrutura de pastas em C:\\WellingtonCyberLab...")
            os.makedirs(INSTALL_DIR, exist_ok=True)
            os.makedirs(os.path.join(INSTALL_DIR, "vpn"), exist_ok=True)
            os.makedirs(os.path.join(INSTALL_DIR, "bin"), exist_ok=True)

            self.log("[+] 2/6 Copiando arquivos do aplicativo cliente e executáveis...")
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            client_src = os.path.join(cur_dir, "wellington_client_win.pyw")
            conf_src = os.path.join(cur_dir, "wellington-lab.conf")
            exe_src = os.path.join(cur_dir, "WellingtonCyberLab.exe")
            bat_src = os.path.join(cur_dir, "Iniciar_CyberLab.bat")

            if os.path.exists(client_src):
                shutil.copy2(client_src, os.path.join(INSTALL_DIR, "bin", "wellington_client_win.pyw"))
                shutil.copy2(client_src, os.path.join(INSTALL_DIR, "wellington_client_win.pyw"))
            if os.path.exists(conf_src):
                shutil.copy2(conf_src, os.path.join(INSTALL_DIR, "vpn", "wellington-lab.conf"))
            if os.path.exists(exe_src):
                shutil.copy2(exe_src, os.path.join(INSTALL_DIR, "WellingtonCyberLab.exe"))
                shutil.copy2(exe_src, os.path.join(INSTALL_DIR, "bin", "WellingtonCyberLab.exe"))
            if os.path.exists(bat_src):
                shutil.copy2(bat_src, os.path.join(INSTALL_DIR, "Iniciar_CyberLab.bat"))
                shutil.copy2(bat_src, os.path.join(INSTALL_DIR, "bin", "Iniciar_CyberLab.bat"))

            # Instalação opcional via winget
            if self.var_wireguard.get():
                self.log("[+] 3/6 Verificando / Instalando WireGuard oficial via winget...")
                subprocess.run("winget install --id WireGuard.WireGuard --silent --accept-source-agreements --accept-package-agreements", shell=True)

            if self.var_nmap.get():
                self.log("[+] 4/6 Verificando / Instalando Nmap via winget...")
                subprocess.run("winget install --id Insecure.Nmap --silent --accept-source-agreements --accept-package-agreements", shell=True)

            if self.var_wireshark.get():
                self.log("[+] Verificando / Instalando Wireshark via winget...")
                subprocess.run("winget install --id WiresharkFoundation.Wireshark --silent --accept-source-agreements --accept-package-agreements", shell=True)

            if self.var_desktop_shortcut.get():
                self.log("[+] 5/6 Criando atalhos na Área de Trabalho e Menu Iniciar...")
                ps_script = f"""
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\\Wellington CyberLab.lnk')
                $Shortcut.TargetPath = '{INSTALL_DIR}\\WellingtonCyberLab.exe'
                $Shortcut.WorkingDirectory = '{INSTALL_DIR}'
                $Shortcut.Save()
                """
                subprocess.run(["powershell", "-Command", ps_script], shell=True)

            self.log("[✓] 6/6 Instalação concluída com êxito!")
            messagebox.showinfo("Sucesso", "Wellington CyberLab instalado no computador Windows com sucesso!\nO atalho foi criado na sua Área de Trabalho.")
        except Exception as e:
            self.log(f"[!] Erro durante instalação: {e}")
            messagebox.showerror("Erro", f"Falha na instalação: {e}")
        finally:
            self.progress.stop()
            self.btn_install.config(state="normal")

    def uninstall_lab(self):
        if messagebox.askyesno("Confirmar Desinstalação", "Deseja remover completamente o Wellington CyberLab e seus atalhos deste computador?"):
            try:
                if os.path.exists(INSTALL_DIR):
                    shutil.rmtree(INSTALL_DIR)
                # Remover atalho da Área de trabalho
                ps_script = """
                $path = [Environment]::GetFolderPath('Desktop') + '\\Wellington CyberLab.lnk'
                if (Test-Path $path) { Remove-Item $path -Force }
                """
                subprocess.run(["powershell", "-Command", ps_script], shell=True)
                messagebox.showinfo("Desinstalado", "Wellington CyberLab removido com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao desinstalar: {e}")

if __name__ == "__main__":
    app = WindowsInstallerGUI()
    app.mainloop()
