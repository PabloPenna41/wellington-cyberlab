#!/usr/bin/env bash
# ==============================================================================
# Wellington CyberLab — Script Automatizado de Configuração da Fase 1
# Executa a instalação de pacotes, deploy do site e configuração do Nginx.
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CYBERLAB_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SRV_PUBLIC_DIR="/srv/http/wellington-cyberlab/public"

echo "=========================================================="
echo "    Wellington CyberLab — Configuração Automatizada Fase 1"
echo "=========================================================="

# 1. Verificar permissões de superusuário
if [ "$EUID" -ne 0 ]; then
    echo "[-] Erro: Este script precisa de privilégios de root para instalar pacotes e configurar /srv e /etc."
    echo "    Execute: sudo bash $0"
    exit 1
fi

# 2. Instalação do Nginx e utilitários de rede essenciais
echo "[+] 1/5 Instalando Nginx e ferramentas essenciais..."
pacman -S --needed --noconfirm nginx curl

# 3. Preparação do diretório web em /srv/http
echo "[+] 2/5 Preparando diretório de publicação (/srv/http/wellington-cyberlab)..."
mkdir -p "$SRV_PUBLIC_DIR"
cp -r "$CYBERLAB_ROOT/website/public"/* "$SRV_PUBLIC_DIR/"
chown -R http:http /srv/http/wellington-cyberlab
chmod -R 755 /srv/http/wellington-cyberlab

# 4. Configuração do Nginx para o site institucional Wellington Negócios
echo "[+] 3/5 Configurando Nginx para o site Wellington Negócios..."
mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled

cat << 'EOF' > /etc/nginx/sites-available/wellington-public.conf
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name localhost 127.0.0.1 192.168.1.6;

    root /srv/http/wellington-cyberlab/public;
    index index.html;

    # Cabeçalhos de segurança (Hardening)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Logs
    access_log /var/log/nginx/wellington_access.log;
    error_log /var/log/nginx/wellington_error.log;
}
EOF

ln -sf /etc/nginx/sites-available/wellington-public.conf /etc/nginx/sites-enabled/wellington-public.conf

# Garantir que o nginx.conf padrão inclua a pasta sites-enabled
if ! grep -q "sites-enabled" /etc/nginx/nginx.conf; then
    sed -i '/http {/a \    include /etc/nginx/sites-enabled/*.conf;' /etc/nginx/nginx.conf
fi

# 5. Validar sintaxe do Nginx
echo "[+] 4/5 Validando sintaxe da configuração do Nginx..."
nginx -t

# 6. Habilitar e iniciar o Nginx
echo "[+] 5/5 Ativando serviço Nginx..."
systemctl daemon-reload
systemctl enable --now nginx
systemctl restart nginx

# 7. Liberar porta 80 no UFW temporariamente (para permitir testes na LAN até a Fase 2)
if command -v ufw >/dev/null 2>&1; then
    echo "[+] Ajustando regra preliminar de acesso local no UFW (porta 80/tcp)..."
    ufw allow 80/tcp comment 'Wellington CyberLab - HTTP Public' || true
fi

echo "=========================================================="
echo "    Fase 1 Concluída com Sucesso!"
echo "=========================================================="
curl -s -I http://127.0.0.1 | head -n 5
echo "O site Wellington Negócios está online e funcional em http://127.0.0.1"
