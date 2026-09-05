#!/bin/bash
# deploy/install_app.sh
# Run this after uploading code to /home/notifi/app/
# Run as: root or notifi user

set -e

APP_DIR="/home/notifi/app"
VENV="/home/notifi/venv"

echo "============================================"
echo "  Installing Notifi Application"
echo "============================================"

cd $APP_DIR

# manage.py needs the real DB/secret values from /home/notifi/.env.
# systemd's EnvironmentFile= loads these automatically for the running
# service, but a plain `sudo -u notifi ... manage.py` does NOT — the
# .env file has to be sourced into the shell explicitly first.
run_manage() {
    sudo -u notifi bash -c "
        set -a
        source /home/notifi/.env
        set +a
        cd $APP_DIR
        $VENV/bin/python manage.py $*
    "
}

# Install Python dependencies
echo "[1/6] Installing Python packages..."
sudo -u notifi $VENV/bin/pip install --upgrade pip
sudo -u notifi $VENV/bin/pip install -r requirements.txt
echo "Packages installed."

# Run database migrations
echo "[2/6] Running database migrations..."
run_manage migrate --noinput
echo "Migrations complete."

# Collect static files
echo "[3/6] Collecting static files..."
run_manage collectstatic --noinput
echo "Static files collected."

# Seed initial data (only on first install)
echo "[4/6] Seeding database..."
run_manage seed_notifi || echo "Seed already done or failed — continuing."

# Install systemd service
echo "[5/6] Installing systemd service..."
cp $APP_DIR/deploy/notifi.service /etc/systemd/system/notifi.service
systemctl daemon-reload
systemctl enable notifi
systemctl start notifi
systemctl status notifi --no-pager
echo "Gunicorn service running."

# Install Nginx config
# If the SSL certificate doesn't exist yet, deploy/nginx_notifi.conf would
# fail `nginx -t` (it references cert files that ssl_setup.sh hasn't
# created yet). Fall back to a temporary HTTP-only proxy config so the app
# is reachable immediately; ssl_setup.sh swaps in the full HTTPS config
# once DNS points here and certbot succeeds.
echo "[6/6] Installing Nginx config..."
if [ -f "/etc/letsencrypt/live/notifi.co.tz/fullchain.pem" ]; then
    cp $APP_DIR/deploy/nginx_notifi.conf /etc/nginx/sites-available/notifi
    echo "HTTPS config installed (certificate already present)."
else
    cat > /etc/nginx/sites-available/notifi << 'NGINXEOF'
server {
    listen 80;
    listen [::]:80;
    server_name notifi.co.tz www.notifi.co.tz;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    client_max_body_size 10M;

    location /static/ {
        alias /home/notifi/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://127.0.0.1:8002;
    }
}
NGINXEOF
    echo "Temporary HTTP-only config installed — run ssl_setup.sh once DNS points here."
fi
ln -sf /etc/nginx/sites-available/notifi /etc/nginx/sites-enabled/notifi
nginx -t && systemctl reload nginx
echo "Nginx configured."

echo ""
echo "============================================"
echo "  App installed! Next: run ssl_setup.sh"
echo "  (once notifi.co.tz DNS points to this server)"
echo "============================================"
