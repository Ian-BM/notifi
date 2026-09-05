#!/bin/bash
# deploy/upload_to_server.sh
# Run this from your LOCAL MACHINE to upload code to server

SERVER_IP="167.86.82.106"
SERVER_USER="root"
APP_DIR="/home/notifi/app"

echo "Uploading Notifi to server..."

# Sync files (excludes venv, cache, local db)
rsync -avz \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude 'db.sqlite3' \
    --exclude 'staticfiles/' \
    --exclude '.git/' \
    --exclude 'node_modules/' \
    ./ $SERVER_USER@$SERVER_IP:$APP_DIR/

echo "Upload complete!"
echo "Now SSH in and run: bash $APP_DIR/deploy/install_app.sh"
