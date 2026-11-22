# Cloud computing concepts in CivicPulse

## What the local prototype demonstrates
- A browser-based multi-layer application: frontend, Django server, authentication, ORM and persistent database.
- Resource separation and a replaceable database URL.
- Optional external map tiles; these are not the same as hosting the application in a cloud.
- Role-based access control, stored records and application-level analytics.

## Proposed cloud concepts (not already configured)
- **Cloud computing:** on-demand compute, storage and managed services over a network.
- **IaaS:** virtual machines and networks provide infrastructure control; the team manages more of the software stack.
- **PaaS:** a platform such as Elastic Beanstalk or Azure App Service manages much of the runtime/hosting layer.
- **SaaS:** a complete provider-hosted application consumed through a browser; CivicPulse would only become a SaaS offering if operated and supported as a service.
- **Public cloud:** shared provider infrastructure with tenant isolation. **Private cloud:** cloud environment dedicated to one organization. **Hybrid cloud:** connected private/on-premises and public-cloud environments. **Community cloud:** infrastructure shared by organizations with common needs.
- **Scalability:** increasing capacity as demand grows. **Elasticity:** capacity expands/contracts as demand changes.
- **Availability and reliability:** design for uptime, health monitoring, redundancy and recovery; they are goals, not guarantees.
- **Centralized database:** a managed database gives the app a shared source of truth for multiple users and app instances.
- **Object storage:** S3 or Azure Blob can store image objects independently of app servers.
- **Security:** authentication verifies identity; authorization checks permissions. Use TLS/HTTPS, secret management, least privilege, validation and secure cookies.
- **Monitoring/backups/disaster recovery:** collect logs and metrics, back up data, and periodically test restoration.
- **Resource sharing/cost efficiency:** managed and shared infrastructure can reduce upfront hardware costs, but usage and configuration may still cost money.
- **Vendor lock-in/portability:** provider-specific APIs can make migration harder. The Django ORM (SQLite, PostgreSQL or MySQL via `DATABASE_URL`), standard SQL, environment-based configuration and documented interfaces improve portability.

## Proposed AWS mapping
Route 53 (optional DNS) → CloudFront (optional CDN) → Elastic Beanstalk / app hosting → RDS database + S3 images; IAM controls service permissions; CloudWatch collects logs/metrics; HTTPS protects traffic.

## Proposed Azure mapping
Azure App Service → Azure Database for PostgreSQL → Azure Blob Storage; Microsoft Entra ID may support organization identity needs; Azure Monitor provides observability; HTTPS protects traffic.

These are architecture proposals only. The current project is not deployed to AWS or Azure.
