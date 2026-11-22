# Deploying CivicPulse on AWS EC2 (step by step)

Target setup: **Browser → Nginx (port 80) → Gunicorn (127.0.0.1:8000) → Django → SQLite/RDS**.
Works on Ubuntu 22.04/24.04 and Amazon Linux 2023.

## Why you saw `ERR_CONNECTION_TIMED_OUT`

"Timed out" means your packets never reached a listening program — **the connection was silently dropped on the way**. That is almost always one of the AWS items in section B, not a bug in Django. (A Django/app problem shows a page such as 400, 403, 500 or "connection refused", never a timeout.)

## A. First-time deployment

1. **Launch the instance** (EC2 → Launch instance): Ubuntu 24.04, `t2.micro`/`t3.micro`, *Auto-assign public IP = Enable*.
2. **Security group** – add inbound rules **SSH (22) from My IP** and **HTTP (80) from 0.0.0.0/0**. (Add HTTPS 443 only after step 8.)
3. **Upload the project** (zip → `scp`, or `git clone`), then SSH in:
   ```bash
   ssh -i your-key.pem ubuntu@<PUBLIC-IP>
   unzip CivicPulse_Django.zip && cd civicpulse_django
   ```
4. **Run the installer** (installs everything, creates `.env`, starts the services):
   ```bash
   bash deploy/setup_ec2.sh
   ```
5. **Create the administrator**:
   ```bash
   source .venv/bin/activate
   python manage.py create_admin
   ```
6. **Open** `http://<PUBLIC-IP>/` (type `http://`, not `https://`).
7. *(Optional)* sample record: `python manage.py seed_demo`.
8. *(Optional, later)* HTTPS: point a domain at the instance, install a certificate (e.g. `sudo apt install certbot python3-certbot-nginx` → `sudo certbot --nginx`), open port 443 in the security group, then set `USE_HTTPS=1` and your domain in `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` in `.env` and `sudo systemctl restart civicpulse`.

## B. Fixing `ERR_CONNECTION_TIMED_OUT` (check in this order)

| # | Check | How to fix |
|---|---|---|
| 1 | **Instance is running** and has a **public IPv4** | EC2 console → Instances → state *Running*; *Public IPv4 address* column not empty. |
| 2 | **You are using the current IP** | The public IP **changes every stop/start**. Copy it again from the console, or attach an **Elastic IP** (EC2 → Elastic IPs → Allocate → Associate). |
| 3 | **Security group allows the port** | Instance → *Security* tab → click the group → *Edit inbound rules* → add **HTTP, TCP 80, 0.0.0.0/0**. (If you run gunicorn directly on 8000 you need **Custom TCP 8000** instead.) This is the #1 cause. |
| 4 | **http:// not https://** | Browsers may auto-upgrade; port 443 is closed until step A8. Type `http://<IP>/` explicitly. |
| 5 | **App really listening on 0.0.0.0/80** | On the server run `bash deploy/check_server.sh`. For a quick manual test: `gunicorn config.wsgi:application --bind 0.0.0.0:8000` (never `runserver` on 127.0.0.1). |
| 6 | **OS firewall** | `sudo ufw status` – if active: `sudo ufw allow 80/tcp`. |
| 7 | **Subnet networking** (rare) | VPC → the instance's subnet → *Route table* has `0.0.0.0/0 → igw-…`; *Network ACL* allows inbound 80 and outbound ephemeral ports 1024-65535. |
| 8 | **Your own network** | Some college/corporate Wi-Fi blocks unusual ports. Test from mobile data. PowerShell: `Test-NetConnection <IP> -Port 80`. |

`bash deploy/check_server.sh` (run on the instance) tests services, ports, local HTTP, `ALLOWED_HOSTS` and `ufw` and prints the exact line that fails. If **everything passes there** but the browser still times out, the cause is #2, #3, #4 or #7 – i.e. AWS, not the server.

### Other errors you may meet after it connects
| Symptom | Cause / fix |
|---|---|
| `Bad Request (400)` | The address you typed is not in `ALLOWED_HOSTS` → `bash deploy/setup_ec2.sh` again (it adds the current IP) or edit `.env`. |
| `CSRF verification failed` | Add `CSRF_TRUSTED_ORIGINS=http://<IP>` (or `https://your-domain`) to `.env`, restart. |
| `502 Bad Gateway` | gunicorn is down: `sudo systemctl status civicpulse`, `sudo journalctl -u civicpulse -n 50`. |
| Login works then logs out immediately | `USE_HTTPS=1` was set without HTTPS. Set `USE_HTTPS=0`. |
| `413 Request Entity Too Large` | Photo > 6 MB (nginx limit is 6 MB, app limit 5 MB). |
| `SECRET_KEY is not set` | `.env` missing → run `bash deploy/setup_ec2.sh`. |

## C. Operating it

```bash
sudo systemctl restart civicpulse      # after changing .env or code
sudo systemctl status civicpulse nginx
sudo journalctl -u civicpulse -f       # live application log
bash deploy/setup_ec2.sh               # safe to re-run after updating code (migrates, collects static, restarts)
```
Back up `instance/civicpulse.sqlite3` and `uploads/` (or use RDS + snapshots). Stop the instance when not demonstrating to avoid charges, and remember the public IP changes unless you use an Elastic IP.

## D. Using Amazon RDS (PostgreSQL) instead of SQLite
1. Create an RDS PostgreSQL instance; its security group must allow **TCP 5432 from the EC2 instance's security group**.
2. In `.env`: `DATABASE_URL=postgres://USER:PASSWORD@<endpoint>.rds.amazonaws.com:5432/civicpulse`
3. `bash deploy/setup_ec2.sh` (it installs the PostgreSQL driver and migrates).

## E. Elastic Beanstalk (alternative)
Zip the project root (with `requirements.txt`), create a *Python* platform environment, and set the environment properties `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS=<env-domain>`. WSGI path: `config.wsgi:application`. Uploaded photos on Beanstalk's local disk are not persistent; use S3 before relying on it.

## Honest limitations
Classroom prototype: no email verification, password reset or rate limiting; photos stay on the instance's disk (S3 is only proposed); nothing here has been security-certified.
