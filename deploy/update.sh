#!/bin/bash
# deploy/update.sh
# Run this every time you push code updates
# Usage: bash deploy/update.sh

set -e

APP_DIR="/home/notifi/app"
VENV="/home/notifi/venv"

echo "============================================"
echo "  Updating Notifi — $(date)"
echo "============================================"

cd $APP_DIR

# manage.py needs the real DB/secret values from /home/notifi/.env —
# source it explicitly, since only the systemd service loads it
# automatically (via EnvironmentFile=).
run_manage() {
    sudo -u notifi bash -c "
        set -a
        source /home/notifi/.env
        set +a
        cd $APP_DIR
        $VENV/bin/python manage.py $*
    "
}

# Pull latest code (if using git)
# git pull origin main

# Install any new packages
echo "[1/4] Installing packages..."
sudo -u notifi $VENV/bin/pip install -r requirements.txt --quiet

# Run migrations
echo "[2/4] Running migrations..."
run_manage migrate --noinput

# Collect static files
echo "[3/4] Collecting static files..."
run_manage collectstatic --noinput

# Restart app gracefully
echo "[4/4] Restarting application..."
systemctl restart notifi
systemctl reload nginx

echo ""
echo "Update complete! Site is live."
echo "Check status: systemctl status notifi"
