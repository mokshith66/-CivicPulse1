# Optional cloud deployment proposal

The app is designed to run locally without cloud credentials. No cloud resources are created by this project. Hosting, managed databases, object storage, domains and data transfer may incur charges; check current provider pricing and student credits before provisioning anything.

## Example AWS architecture
1. Run the Django application on an Amazon EC2 instance (Nginx on port 80 → Gunicorn → Django). `deploy/setup_ec2.sh` automates this; see `docs/AWS_DEPLOYMENT.md`. AWS Elastic Beanstalk is an alternative managed option.
2. Set a strong `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, and `DEBUG=0` as environment variables (the `.env` file or platform settings).
3. Use Amazon RDS (PostgreSQL) for a managed relational database: install `requirements-postgres.txt` and set `DATABASE_URL`.
4. Store uploaded images in private Amazon S3 and store object keys in the database; use IAM roles instead of long-lived access keys.
5. Use HTTPS via the hosting platform/load balancer and optionally CloudFront; Route 53 is only needed if using a custom domain.
6. Use CloudWatch for logs/metrics and configure managed database backups.
7. Schema changes are handled with Django migrations (`makemigrations` / `migrate`).

## Example Azure architecture
- Azure App Service for Django hosting.
- Azure Database for PostgreSQL or another supported managed database.
- Azure Blob Storage for private image uploads.
- Microsoft Entra ID for workforce/admin identity integration where appropriate; the app's current local account system is separate.
- Azure Monitor for logs/metrics.
- HTTPS and managed backups.

## Before deployment
- Never deploy with the local demo secret key.
- Set debug off, use HTTPS, configure secure session cookies, apply least-privilege cloud access and private storage.
- Move uploaded images to object storage; local disk may be ephemeral on hosted platforms.
- Add database migrations, rate limiting, email verification/password reset, operational alerts and backup restoration testing.
- Verify current provider instructions and pricing because service settings change.
