#!/usr/bin/env bash
# =============================================================================
# CivicPulse – one-command setup for a fresh EC2 instance (Ubuntu 22.04/24.04
# or Amazon Linux 2023).  Safe to re-run after you update the code.
#
#   cd civicpulse_django
#   bash deploy/setup_ec2.sh
#
# Result:  nginx (port 80)  ->  gunicorn (127.0.0.1:8000)  ->  Django
# =============================================================================
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_USER="$(id -un)"
SERVICE="civicpulse"
cd "$APP_DIR"

say() { printf '\n\033[1;36m== %s\033[0m\n' "$*"; }

if [ "$(id -u)" -eq 0 ]; then
  echo "Run this as your normal user (ubuntu / ec2-user), not root. It uses sudo where needed."; exit 1
fi

# ---- 1. system packages -------------------------------------------------------
say "1/7  Installing system packages"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-venv python3-pip nginx curl
  PY=python3; NGINX_USER=www-data
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y python3.11 python3.11-pip nginx curl
  PY=python3.11; NGINX_USER=nginx
else
  echo "Unsupported OS (need apt-get or dnf)."; exit 1
fi
$PY - <<'PYEOF' || { echo "Python 3.10+ is required."; exit 1; }
import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)
PYEOF

# ---- 2. find this server's public address ------------------------------------
say "2/7  Detecting public IP"
TOKEN="$(curl -s -m 3 -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' || true)"
imds() { curl -s -m 3 -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/$1" || true; }
PUBLIC_IP="$(imds public-ipv4)"
PUBLIC_DNS="$(imds public-hostname)"
[ -z "$PUBLIC_IP" ] && PUBLIC_IP="$(curl -s -m 5 https://checkip.amazonaws.com | tr -d '[:space:]' || true)"
echo "Public IP: ${PUBLIC_IP:-unknown}   DNS: ${PUBLIC_DNS:-none}"

# ---- 3. virtualenv + dependencies ---------------------------------------------
say "3/7  Python environment"
[ -d .venv ] || $PY -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q
if grep -qE '^DATABASE_URL=postgres' .env 2>/dev/null; then
  .venv/bin/pip install -r requirements-postgres.txt -q
fi

# ---- 4. .env -------------------------------------------------------------------
say "4/7  Configuration (.env)"
HOSTS="localhost,127.0.0.1"
[ -n "$PUBLIC_IP" ]  && HOSTS="$PUBLIC_IP,$HOSTS"
[ -n "$PUBLIC_DNS" ] && HOSTS="$PUBLIC_DNS,$HOSTS"
if [ ! -f .env ]; then
  SECRET="$(.venv/bin/python -c 'from django.core.management.utils import get_random_secret_key as g; print(g())')"
  cat > .env <<ENVEOF
SECRET_KEY='$SECRET'
DEBUG=0
ALLOWED_HOSTS=$HOSTS
CSRF_TRUSTED_ORIGINS=${PUBLIC_IP:+http://$PUBLIC_IP}
USE_HTTPS=0
MAX_CONTENT_LENGTH=5242880
TIME_ZONE=Asia/Kolkata
ENVEOF
  chmod 600 .env
  echo "Created .env with a fresh SECRET_KEY."
else
  # Re-run after a stop/start: the public IP may have changed, so make sure it is allowed.
  .venv/bin/python - "$HOSTS" <<'PYEOF'
import sys, re, pathlib
new = [h for h in sys.argv[1].split(",") if h]
p = pathlib.Path(".env"); text = p.read_text()
m = re.search(r"^ALLOWED_HOSTS=(.*)$", text, re.M)
cur = [h.strip() for h in m.group(1).split(",") if h.strip()] if m else []
merged = cur + [h for h in new if h not in cur]
line = "ALLOWED_HOSTS=" + ",".join(merged)
text = re.sub(r"^ALLOWED_HOSTS=.*$", line, text, flags=re.M) if m else text.rstrip("\n") + "\n" + line + "\n"
p.write_text(text); print("Updated:", line)
PYEOF
fi

# ---- 5. database + static files -----------------------------------------------
say "5/7  Database migrate + collectstatic"
mkdir -p instance uploads
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput -v 0
.venv/bin/python manage.py check

# ---- 6. gunicorn as a systemd service ------------------------------------------
say "6/7  gunicorn service"
sudo tee /etc/systemd/system/$SERVICE.service >/dev/null <<UNIT
[Unit]
Description=CivicPulse (gunicorn)
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60 --access-logfile - --error-logfile -
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE >/dev/null
sudo systemctl restart $SERVICE

# ---- 7. nginx on port 80 --------------------------------------------------------
say "7/7  nginx reverse proxy on port 80"
[ -f /etc/nginx/nginx.conf.civicpulse-backup ] || sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.civicpulse-backup
sudo tee /etc/nginx/nginx.conf >/dev/null <<'NGINX'
user __NGINX_USER__;
worker_processes auto;
pid /run/nginx.pid;
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    server_tokens off;
    client_max_body_size 6m;
    access_log /var/log/nginx/access.log;
    error_log  /var/log/nginx/error.log;

    server {
        listen 80 default_server;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 60s;
        }
    }
}
NGINX
sudo sed -i "s/__NGINX_USER__/$NGINX_USER/" /etc/nginx/nginx.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx >/dev/null
sudo systemctl restart nginx

# OS firewall (Ubuntu's ufw): only matters if it is switched on.
if command -v ufw >/dev/null 2>&1 && sudo ufw status | grep -q "Status: active"; then
  sudo ufw allow 22/tcp >/dev/null; sudo ufw allow 80/tcp >/dev/null
  echo "ufw: allowed ports 22 and 80"
fi

# ---- verify ---------------------------------------------------------------------
say "Self-test (from inside the server)"
sleep 2
for url in http://127.0.0.1:8000/health/ http://127.0.0.1/health/; do
  code="$(curl -s -o /dev/null -w '%{http_code}' -m 5 "$url" || echo 000)"
  printf '%-34s -> HTTP %s\n' "$url" "$code"
done

cat <<DONE

----------------------------------------------------------------------
 Server side is ready.  Open:   http://${PUBLIC_IP:-<your-public-ip>}/

 If the browser says "This site can't be reached / ERR_CONNECTION_TIMED_OUT"
 while the two checks above show HTTP 200, the server is fine and AWS is
 blocking the traffic:  EC2 -> Instances -> your instance -> Security tab ->
 Security group -> Edit inbound rules -> add  HTTP | TCP | 80 | 0.0.0.0/0
 (use http:// not https://).  Full checklist: docs/AWS_DEPLOYMENT.md

 Create your administrator account:
     cd $APP_DIR && source .venv/bin/activate && python manage.py create_admin
----------------------------------------------------------------------
DONE
