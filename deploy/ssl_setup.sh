#!/bin/bash
# deploy/ssl_setup.sh
# Run AFTER install_app.sh
# Make sure notifi.co.tz DNS is pointing to this server first

set -e

DOMAIN="notifi.co.tz"
EMAIL="ianbethuel4@gmail.com"

echo "============================================"
echo "  Setting up SSL for $DOMAIN"
echo "============================================"

echo "Checking DNS resolution..."
# Query a public resolver directly (bypasses local/systemd-resolved cache,
# which can lag behind real propagation) and force IPv4 for both sides —
# ifconfig.me returns IPv6 if the host has it, which will never match an
# A record and produces a false "DNS not ready" failure.
RESOLVED_IP=$(dig +short $DOMAIN @8.8.8.8 A | tail -1)
SERVER_IP=$(curl -s -4 ifconfig.me)

echo "Domain resolves to: $RESOLVED_IP"
echo "This server IP: $SERVER_IP"

if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo ""
    echo "WARNING: DNS not pointing to this server yet!"
    echo "Update your domain DNS A record to: $SERVER_IP"
    echo "Then wait 30-60 minutes and run this script again."
    exit 1
fi

echo "DNS OK. Installing SSL certificate..."

# Temporarily use HTTP-only config for certbot verification
cat > /etc/nginx/sites-available/notifi_temp << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    location / {
        return 200 'SSL setup in progress';
        add_header Content-Type text/plain;
    }
}
EOF

ln -sf /etc/nginx/sites-available/notifi_temp /etc/nginx/sites-enabled/notifi
nginx -t && systemctl reload nginx

# Get certificate
certbot certonly \
    --webroot \
    --webroot-path /var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

# Switch to full HTTPS config. The sites-enabled symlink was pointed at
# notifi_temp above for the ACME challenge — repoint it back to notifi
# now, or nginx keeps serving the temporary placeholder forever.
cp /home/notifi/app/deploy/nginx_notifi.conf /etc/nginx/sites-available/notifi
ln -sf /etc/nginx/sites-available/notifi /etc/nginx/sites-enabled/notifi
nginx -t && systemctl reload nginx

# Setup auto-renewal
echo "0 12 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'" \
    > /etc/cron.d/certbot-notifi

echo ""
echo "============================================"
echo "  SSL installed successfully!"
echo "  Notifi is now live at https://$DOMAIN"
echo "============================================"
