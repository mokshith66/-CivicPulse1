# Feature status

## Implemented in source (verify locally)
- Citizen registration/login/logout and profile name editing.
- Password hashing, sessions, CSRF protection and server-side admin authorization.
- Complaint creation, unique ID, optional photo, coordinate validation, status/priority, history.
- Citizen ownership checks, complaint detail/tracking, map and filters.
- Admin dashboard, review/update/delete test records, database-backed charts.
- SQLite default (PostgreSQL/RDS via `DATABASE_URL`), Django migrations, custom 403/404/500 pages, Django test suite and local setup docs.
- Optional EC2 deployment tooling: Gunicorn + Nginx + systemd (`deploy/setup_ec2.sh`, `deploy/check_server.sh`). Deployment on AWS itself must still be performed and verified by you.

## Proposed / not implemented
- AWS/Azure provisioning or live deployment.
- S3/Azure Blob upload integration, managed database provisioning, CloudFront/Route 53, CloudWatch/Azure Monitor configuration.
- Email/SMS notifications, password reset, email verification, rate limiting, and security certification.
