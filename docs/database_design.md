# Database design

## Entities
- **User**: account identity, password hash, role and creation timestamp.
- **Complaint**: complaint ID, citizen foreign key, category, title, description, location, optional coordinates/photo, status, priority, admin note and timestamps.
- **ComplaintHistory**: audit trail for initial submission and meaningful administrative status/note changes.

## Relationships
- One User can submit many Complaints.
- One Complaint can have many ComplaintHistory entries.
- `complaint_id` and `User.email` are unique.
- Foreign keys connect complaint to submitter and history to complaint and actor.

## ER diagram (Mermaid)
```mermaid
erDiagram
    USER ||--o{ COMPLAINT : submits
    COMPLAINT ||--o{ COMPLAINT_HISTORY : records
    USER ||--o{ COMPLAINT_HISTORY : changes
    USER {
      int id PK
      string name
      string email UK
      string password_hash
      string role
      datetime created_at
    }
    COMPLAINT {
      int id PK
      string complaint_id UK
      int user_id FK
      string category
      string title
      text description
      string location
      float latitude
      float longitude
      string status
      string priority
      datetime created_at
      datetime updated_at
    }
    COMPLAINT_HISTORY {
      int id PK
      int complaint_pk FK
      string previous_status
      string new_status
      text note
      int changed_by FK
      datetime changed_at
    }
```

Tables are created and versioned with Django migrations (`python manage.py migrate`; the initial migration is `complaints/migrations/0001_initial.py`). After any model change run `python manage.py makemigrations` and then `migrate`. In the Django models the foreign keys are named `complaint` (history → complaint) and `changed_by`; `ComplaintHistory.changed_by` is set to NULL if that user is later removed.
