#!/usr/bin/env bash
# Run ON the EC2 instance to find out why the site is not reachable:
#   bash deploy/check_server.sh
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ok()   { printf '  \033[32m[ OK ]\033[0m %s\n' "$*"; }
bad()  { printf '  \033[31m[FAIL]\033[0m %s\n' "$*"; }
info() { printf '  \033[33m[ i ]\033[0m %s\n' "$*"; }

echo "1) Services"
for s in civicpulse nginx; do
  if systemctl is-active --quiet $s; then ok "$s is running"; else bad "$s is NOT running  ->  sudo systemctl status $s"; fi
done

echo "2) Listening ports"
ss -ltn 2>/dev/null | grep -qE ':80\s'   && ok "something listens on :80 (nginx)"   || bad "nothing listens on port 80"
ss -ltn 2>/dev/null | grep -qE ':8000\s' && ok "gunicorn listens on :8000"           || bad "nothing listens on port 8000"

echo "3) Local HTTP tests (these never touch the AWS firewall)"
for u in http://127.0.0.1:8000/health/ http://127.0.0.1/health/; do
  c=$(curl -s -o /dev/null -w '%{http_code}' -m 5 "$u" || echo 000)
  [ "$c" = "200" ] && ok "$u -> 200" || bad "$u -> $c"
done

echo "4) Public address"
TOKEN=$(curl -s -m 3 -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60')
IP=$(curl -s -m 3 -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)
if [ -z "$IP" ]; then bad "instance has NO public IPv4 (enable auto-assign public IP or attach an Elastic IP)"
else
  info "current public IP: $IP   <- use exactly this in the browser: http://$IP/"
  info "it changes every time the instance is stopped/started unless you attach an Elastic IP"
  if grep -q "^ALLOWED_HOSTS=.*$IP" "$APP_DIR/.env" 2>/dev/null; then ok "IP is listed in ALLOWED_HOSTS"
  else bad "IP missing from ALLOWED_HOSTS in .env  ->  re-run: bash deploy/setup_ec2.sh"; fi
fi

echo "5) OS firewall"
if command -v ufw >/dev/null && sudo ufw status | grep -q "Status: active"; then
  sudo ufw status | grep -qE '^80(/tcp)?\s+ALLOW' && ok "ufw allows 80" || bad "ufw is active but port 80 is not allowed -> sudo ufw allow 80/tcp"
else ok "ufw not active"; fi

echo "6) Recent errors"
sudo journalctl -u civicpulse -n 8 --no-pager 2>/dev/null | sed 's/^/    /'
sudo tail -n 5 /var/log/nginx/error.log 2>/dev/null | sed 's/^/    /'

cat <<'TXT'

If 1-5 are all OK but the browser still shows ERR_CONNECTION_TIMED_OUT,
the block is in AWS, not on the server:
  - Security group inbound rule for HTTP (TCP 80) from 0.0.0.0/0 is missing
  - or you are opening a different IP than shown in step 4
  - or you typed https:// (port 443 is closed) instead of http://
  - or the subnet's Network ACL / route table has no internet gateway route
Test from your own PC (PowerShell):  Test-NetConnection <IP> -Port 80
TXT
