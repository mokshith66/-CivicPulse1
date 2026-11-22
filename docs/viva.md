# CivicPulse demo script and viva preparation

## Five-minute demonstration script
**0:00–0:30 — Introduction:** “CivicPulse is an academic prototype for reporting civic issues such as potholes, waste and damaged streetlights. It supports SDG 11 and demonstrates web/cloud concepts; it is not an official government service.”

**0:30–1:15 — Citizen account:** Register or sign in as a citizen. Explain that passwords are hashed and sessions protect authenticated routes.

**1:15–2:00 — Submit a complaint:** Choose a category, add a title, description and location, optionally upload an image, then pin a location or enter coordinates. Submit and point out the unique complaint ID.

**2:00–2:45 — Tracking:** Open the complaint details. Explain current status, priority, latest admin note and status history. Mention that citizens can only access their own complaints.

**2:45–3:45 — Administrator workflow:** Sign out and use the administrator account created through the CLI. Review the complaint, update status/priority and add a note. Show the recorded history.

**3:45–4:20 — Analytics and map:** Show the map marker for geolocated complaints and analytics charts generated from database queries.

**4:20–5:00 — Cloud architecture:** Explain the local prototype uses SQLite and local uploads. In a proposed cloud deployment, app hosting, managed SQL database, object storage, HTTPS, monitoring and backups can be hosted on AWS or Azure. Be explicit that this is proposed, not already deployed.

## Likely viva questions
1. **What problem does CivicPulse address?** It organizes civic reports and lets users track status using complaint IDs.
2. **Why Django?** It is a batteries-included Python framework: ORM, migrations, authentication, form validation, CSRF protection and an admin site are built in, which suits a multi-role application and makes deployment settings (`ALLOWED_HOSTS`, `SECRET_KEY`, static files) explicit.
3. **What is cloud computing?** On-demand access to computing resources and services over a network.
4. **Is your local app already cloud deployed?** No. It runs locally; AWS/Azure deployment is documented as a proposal.
5. **What is the difference between IaaS and PaaS?** IaaS gives more control over virtual infrastructure; PaaS manages more of the runtime/platform.
6. **What is SaaS?** A complete software product accessed by users over a network.
7. **Why use SQLite?** It is simple, file-based and requires no separate database server for a classroom demo.
8. **How are passwords protected?** Django's password hashers (salted PBKDF2-SHA256 by default) store a hash, not the original password.
9. **How is admin access protected?** The server checks the authenticated user's role before serving admin routes.
10. **Why use complaint history?** It provides an audit trail of status changes and notes.
11. **What is object storage?** A service such as S3 or Azure Blob that stores files as objects separately from the relational database.
12. **What does Leaflet do?** It renders interactive maps; OpenStreetMap supplies the map tiles.
13. **What does Chart.js do?** It renders browser charts using values queried from the database.
14. **What are scalability and elasticity?** Scalability means handling more load by adding capacity; elasticity adjusts capacity to demand.
15. **What are the limitations?** No municipal integration, notifications, production cloud deployment, formal security audit or load test yet.
16. **How does this relate to SDG 11?** It demonstrates a civic reporting workflow intended to support sustainable communities.
17. **How can vendor lock-in be reduced?** Use portable frameworks, standard database interfaces, environment-based configuration and document provider-specific dependencies.
