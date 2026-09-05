#!/bin/bash
# deploy/setup_server.sh
# Run this ONCE on a fresh Contabo Ubuntu 22.04/24.04 VPS
# Usage: bash setup_server.sh
# Run as: root

set -e  # Exit on any error

echo "============================================"
echo "  Notifi SMS Platform — Server Setup"
echo "============================================"

# ─── System Update ───────────────────────────────
echo "[1/10] Updating system packages..."
apt update && apt upgrade -y
apt install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx \
    git \
    curl \
    ufw \
    certbot python3-certbot-nginx \
    supervisor \
    htop \
    fail2ban

# ─── Firewall ────────────────────────────────────
echo "[2/10] Configuring firewall..."
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw --force enable
echo "Firewall configured."

# ─── Create system user ──────────────────────────
echo "[3/10] Creating notifi system user..."
if ! id "notifi" &>/dev/null; then
    useradd --system --shell /bin/bash --home /home/notifi --create-home notifi
    echo "User 'notifi' created."
else
    echo "User 'notifi' already exists."
fi

# ─── PostgreSQL Setup ────────────────────────────
echo "[4/10] Setting up PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Generate random DB password
DB_PASSWORD=$(openssl rand -base64 32)

sudo -u postgres psql << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'notifi_user') THEN
        CREATE USER notifi_user WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

CREATE DATABASE notifi_db OWNER notifi_user;
GRANT ALL PRIVILEGES ON DATABASE notifi_db TO notifi_user;
EOF

echo "Database created. Password: $DB_PASSWORD"
echo "SAVE THIS PASSWORD — you'll need it for .env"
echo "DB_PASSWORD=$DB_PASSWORD" >> /root/notifi_credentials.txt

# ─── App Directory ───────────────────────────────
echo "[5/10] Setting up app directory..."
mkdir -p /home/notifi/app
mkdir -p /var/log/notifi
mkdir -p /var/run/notifi
mkdir -p /var/www/certbot

chown -R notifi:notifi /home/notifi
chown -R notifi:notifi /var/log/notifi
chown -R notifi:notifi /var/run/notifi

# ─── Python Virtual Environment ──────────────────
echo "[6/10] Creating Python virtual environment..."
sudo -u notifi python3 -m venv /home/notifi/venv
echo "Virtual environment created at /home/notifi/venv"

# ─── Nginx Setup ─────────────────────────────────
echo "[7/10] Configuring Nginx..."
rm -f /etc/nginx/sites-enabled/default
echo "Default Nginx site disabled."

# ─── Fail2Ban ────────────────────────────────────
echo "[8/10] Configuring Fail2Ban..."
systemctl enable fail2ban
systemctl start fail2ban

# ─── Log Rotation ────────────────────────────────
echo "[9/10] Setting up log rotation..."
cat > /etc/logrotate.d/notifi << 'EOF'
/var/log/notifi/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 notifi notifi
    sharedscripts
    postrotate
        systemctl reload notifi 2>/dev/null || true
    endscript
}
EOF

# ─── Summary ─────────────────────────────────────
echo ""
echo "[10/10] Server setup complete!"
echo "============================================"
echo "  NEXT STEPS:"
echo "============================================"
echo "1. Upload your code to /home/notifi/app/"
echo "2. Create /home/notifi/.env (see deploy/.env.production)"
echo "3. Run: bash deploy/install_app.sh"
echo "4. Run: bash deploy/ssl_setup.sh"
echo ""
echo "Saved credentials: /root/notifi_credentials.txt"
cat /root/notifi_credentials.txt
echo "============================================"
