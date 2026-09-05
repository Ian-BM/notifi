# Notifi Deployment Guide

Target server: Contabo VPS at `167.86.82.106` — Ubuntu 22.04/24.04, domain `notifi.co.tz`.

## First Time Deployment (Fresh Server)

### Step 1: Prepare DNS
Go to your domain registrar (PataHost/Hostraha).
Add an A record:
- Type: A
- Name: @
- Value: 167.86.82.106
- TTL: 3600

Add another A record:
- Type: A
- Name: www
- Value: 167.86.82.106

Wait 30-60 minutes for DNS to propagate.

### Step 2: Setup Server
SSH into your Contabo VPS:
```
ssh root@167.86.82.106
```

Upload the setup script and run it:
```
bash deploy/setup_server.sh
```

Save the generated DB password shown at the end.

### Step 3: Create Environment File
```
cp deploy/.env.production /home/notifi/.env
nano /home/notifi/.env
```

Fill in ALL values:
- SECRET_KEY: generate with `python3 -c "import secrets; print(secrets.token_hex(50))"`
- SERVER_IP: already set to 167.86.82.106
- DB_PASSWORD: the password generated in Step 2
- BEEM_API_KEY: from your Beem dashboard
- BEEM_SECRET_KEY: from your Beem dashboard

### Step 4: Upload Code
From your LOCAL machine:
```
bash deploy/upload_to_server.sh
```

### Step 5: Install App
Back on the server:
```
bash /home/notifi/app/deploy/install_app.sh
```

### Step 6: Install SSL
```
bash /home/notifi/app/deploy/ssl_setup.sh
```

### Step 7: Verify
Open https://notifi.co.tz in your browser.
Login with: admin / notifi2026
CHANGE THIS PASSWORD IMMEDIATELY:
```
cd /home/notifi/app
sudo -u notifi DJANGO_SETTINGS_MODULE=core.settings_production \
    /home/notifi/venv/bin/python manage.py changepassword admin
```

---

## Updating After Code Changes

From your local machine:
```
bash deploy/upload_to_server.sh
```

Then on the server:
```
bash /home/notifi/app/deploy/update.sh
```

---

## Useful Commands on Server

```bash
# Check app status
systemctl status notifi

# View app logs
journalctl -u notifi -f

# View error logs
tail -f /var/log/notifi/django.log

# Restart app
systemctl restart notifi

# Restart Nginx
systemctl restart nginx

# Check Nginx config
nginx -t

# Django shell
cd /home/notifi/app
sudo -u notifi /home/notifi/venv/bin/python manage.py shell

# Manual database backup
sudo -u postgres pg_dump notifi_db > /home/notifi/backup_$(date +%Y%m%d).sql
```

---

## Daily Backup (Optional but Recommended)

Add this to crontab (`crontab -e` as root):
```
0 2 * * * sudo -u postgres pg_dump notifi_db > /home/notifi/backups/notifi_$(date +\%Y\%m\%d).sql 2>/dev/null
0 3 * * * find /home/notifi/backups/ -name "*.sql" -mtime +7 -delete
```

Create the backup directory first: `mkdir -p /home/notifi/backups && chown notifi:notifi /home/notifi/backups`
