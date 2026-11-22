# CivicPulse — Cloud-Based Smart City Issue Reporting System
## Activity-Based Assignment (ABA) Report Draft

**Student name:** [Enter student name]  
**USN:** [Enter USN]  
**Department:** Computer Science and Engineering (Artificial Intelligence and Machine Learning)  
**Semester:** Fifth Semester  
**Subject:** Cloud Computing  
**Institution:** [Enter institution]  
**Guide:** [Enter guide name]  
**Academic year:** [Enter academic year]

> **Implementation accuracy note:** This report is a draft for editing. Mark test outcomes and screenshots only after you have run the application. The included source package proposes AWS/Azure deployment but does not mean that cloud deployment has occurred.

## 1. Abstract
CivicPulse is a web-based prototype for reporting and tracking civic infrastructure issues such as potholes, waste accumulation, damaged streetlights, water leakage and blocked drainage. Citizens can create accounts, submit reports with locations and optional photographs, receive complaint IDs and follow status history. Administrators can review reports, assign priorities, update statuses and examine database-backed analytics. The application uses Django, the Django ORM, SQLite, Bootstrap, Leaflet, OpenStreetMap and Chart.js. It is designed to run locally and describes how the same application could be deployed using cloud hosting, a managed relational database and object storage. The project is aligned with SDG 11 and SDG 9 as an educational prototype, not an official municipal service.

## 2. Introduction
Cities need accessible ways for residents to communicate infrastructure problems. Digital reporting can organize reports, make progress visible and help administrators review issues in one place. CivicPulse demonstrates a basic web workflow using common full-stack technologies.

## 3. Problem statement
Civic issues may be reported through disconnected channels, making it difficult for residents to obtain a reference number or track progress. A centralized reporting prototype can organize issue details and status history.

## 4. Motivation and need
The project provides hands-on practice with web development, authentication, relational data modelling, file handling, maps, charts and cloud architecture. It also demonstrates how a scalable hosted service might support users in different locations.

## 5. Objectives
- Create an accessible interface for reporting civic issues.
- Support complaint IDs and status tracking.
- Provide role-protected administrator tools.
- Persist records and status history in a relational database.
- Visualize mapped complaints and basic statistics.
- Explain cloud deployment options and security considerations.

## 6. Scope
The prototype covers citizen accounts, issue submission, optional image uploads, coordinate entry/map selection, tracking, administrator review, filters, status history and analytics. It does not connect to government systems, dispatch municipal teams, or guarantee real-world resolution.

## 7. Existing system and limitations
Reports may be sent through phone calls, emails, social media or separate portals. Such channels can lack a single reference number or consistent visible history. This is a general motivation, not a claim based on a user survey or measured study.

## 8. Proposed system
CivicPulse provides a web interface backed by a Django application and relational database. Server-side role checks separate citizen and administrator capabilities. Leaflet presents location information and Chart.js renders current database aggregates.

## 9. Functional and non-functional requirements
**Functional:** register/login/logout; submit reports; generate IDs; view own reports; track status; upload allowed images; map coordinates; admin search/filter/update/delete test records; status history; profile name update; analytics.

**Non-functional:** responsive UI; understandable structure; data persistence; basic privacy/access controls; maintainability; user-friendly errors. Production-grade availability and security are not claimed.

## 10. Hardware and software requirements
- Computer with modern browser and internet access for CDN/map resources.
- Python 3.10 or later, pip and virtual environment.
- Django 5.2 LTS (ORM, authentication, forms, CSRF middleware, migrations), Gunicorn, WhiteNoise, python-dotenv, dj-database-url and Pillow. Tests use Django's built-in test runner.
- SQLite for local execution; optional compatible database and storage for cloud deployment.

## 11. System architecture
Browser → responsive HTML/CSS/Bootstrap/JavaScript → Django views/URL routing → authentication and authorization → complaint services → SQLite/managed relational database. Optional image storage is local in the prototype and can be replaced with object storage. Leaflet uses OpenStreetMap tiles; Chart.js displays aggregates. The editable diagram is in `docs/architecture.mmd`.

## 12. Database design and ER diagram
The database contains `User`, `Complaint` and `ComplaintHistory`. One user can submit many complaints; one complaint can have multiple history entries; a user can author multiple history entries. Unique constraints protect email and complaint IDs. See `docs/database_design.md` for the ER diagram.

## 13. Module descriptions
1. Authentication: registration, password hashing, login and session management.
2. Citizen dashboard: personal complaint summary.
3. Complaint submission: category, title, description, location, optional coordinates/photo.
4. Tracking: complaint details and progress history.
5. Administration: status/priority, notes, search, filtering and test-record deletion.
6. Map: display reports with saved coordinates.
7. Analytics: category, status and date-based charts from database queries.
8. Cloud documentation: proposed AWS/Azure architecture and deployment cautions.

## 14. User interface screenshots
**Insert actual screenshots after running the app.** Suggested screenshots: landing page, registration/login, citizen dashboard, report form with map, complaint detail/history, admin dashboard, manage complaints and analytics. Do not use mock screenshots as evidence of a running deployment.

## 15. Cloud computing concepts
Cloud hosting can provide network-accessible compute, managed databases and object storage. IaaS offers greater infrastructure control; PaaS manages more of the application platform; SaaS is a finished service delivered to users. Public, private, hybrid and community clouds differ by access and ownership. Scalability, elasticity, monitoring, backups, centralized data and shared resources can support growth, but require configuration and cost management. The local version demonstrates a layered web application and persistent storage; it does not itself prove cloud hosting. See `docs/cloud_concepts.md`.

## 16. AWS and Azure deployment proposals
A possible AWS design uses Elastic Beanstalk or app hosting, RDS, S3, IAM, CloudWatch, HTTPS, and optionally CloudFront/Route 53. A possible Azure design uses App Service, Azure Database for PostgreSQL, Blob Storage, an appropriate identity service, Azure Monitor and HTTPS. These are proposals only; no cloud resources are configured by this project. Check provider pricing before provisioning resources.

## 17. SDG alignment
- **SDG 11 — Sustainable Cities and Communities:** supports the concept of more inclusive and sustainable communities through an organized civic issue reporting workflow.
- **SDG 9 — Industry, Innovation and Infrastructure:** demonstrates a digital infrastructure concept and practical use of web/cloud technologies.
The project is an educational alignment, not an official UN or municipal partnership.

## 18. Testing methodology and results
Use the test plan in `docs/test_plan.md` and automated tests in `tests/test_app.py`. The test table deliberately leaves actual results and pass/fail unrecorded until tests are run. Insert screenshots or logs only for tests actually performed.

## 19. Limitations
The prototype has no email/SMS notifications, password reset, email verification, advanced moderation, municipal integration or production deployment. Local uploads are not a durable cloud-storage strategy. Extension checks alone are not sufficient for production file security. The prototype has not undergone a security audit or load testing.

## 20. Future enhancements
- Deploy to AWS/Azure with managed database and object storage.
- Add email notifications and verified accounts.
- Add rate limiting, password reset and stronger upload content inspection.
- Add geospatial search, duplicate-report detection and prioritization assistance.
- Add accessibility/usability evaluation and load testing.
- Add migrations, backup restoration drills and monitoring alerts.

## 21. Conclusion
CivicPulse demonstrates an end-to-end civic issue reporting workflow and introduces cloud deployment concepts through a practical software prototype. It combines a relational data model, user roles, complaint tracking, maps and analytics. Cloud deployment, high availability and production security remain future work until configured and verified.

## 22. References
Accessed 17 October 2026; verify pages and URLs before final submission.
1. Django documentation, https://docs.djangoproject.com/
2. Gunicorn documentation, https://docs.gunicorn.org/
3. Bootstrap documentation, https://getbootstrap.com/docs/5.3/
4. Leaflet documentation, https://leafletjs.com/reference.html
5. OpenStreetMap tile usage policy, https://operations.osmfoundation.org/policies/tiles/
6. Chart.js documentation, https://www.chartjs.org/docs/latest/
7. Amazon Web Services, https://aws.amazon.com/
8. Microsoft Azure, https://azure.microsoft.com/
9. United Nations Sustainable Development Goal 9, https://sdgs.un.org/goals/goal9
10. United Nations Sustainable Development Goal 11, https://sdgs.un.org/goals/goal11
