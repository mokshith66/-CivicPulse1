# Manual test plan

Run each test against the local application. Record the actual outcome and pass/fail only after executing it. Automated coverage is in `complaints/tests/test_app.py` (run `python manage.py test`).

| # | Test case | Input/action | Expected result | Actual result | Pass/fail |
|---|---|---|---|---|---|
| 1 | Successful registration | New name, email, 8+ character password | Account saved; citizen dashboard opens | Not run | Not run |
| 2 | Duplicate email | Register same email twice | Duplicate is rejected | Not run | Not run |
| 3 | Valid login | Correct citizen credentials | Login succeeds | Not run | Not run |
| 4 | Invalid login | Incorrect password | Generic error; no login | Not run | Not run |
| 5 | Protected route | Visit `/dashboard` while logged out | Redirect to login | Not run | Not run |
| 6 | Valid complaint | Complete required fields | Unique ID and detail page shown | Not run | Not run |
| 7 | Incomplete complaint | Leave required field empty | Validation prevents save | Not run | Not run |
| 8 | Unique complaint ID | Submit two complaints | IDs differ | Not run | Not run |
| 9 | Citizen data privacy | Log in as citizen A and request citizen B's ID | 403 denied | Not run | Not run |
| 10 | Citizen admin restriction | Citizen opens `/admin` | 403 denied | Not run | Not run |
| 11 | Admin status update | Change status as admin | Status persists | Not run | Not run |
| 12 | Status history | Change status and add note | History row is recorded | Not run | Not run |
| 13 | Search and filters | Filter by ID/category/status | Matching records only | Not run | Not run |
| 14 | Allowed image | Upload JPG/PNG/WEBP under 5 MB | Image saved and viewable to authorized users | Not run | Not run |
| 15 | Invalid/oversized upload | Upload PDF or >5 MB | Rejected with helpful message | Not run | Not run |
| 16 | Map marker | Add valid coordinates | Marker appears | Not run | Not run |
| 17 | Missing coordinates | Submit without coordinates | Map does not crash; record omitted | Not run | Not run |
| 18 | Analytics | Create/change complaints | Counts/charts reflect database | Not run | Not run |
| 19 | Persistence | Restart the server (Gunicorn/`runserver`) | Records remain in SQLite DB | Not run | Not run |
| 20 | Responsive layout | Test mobile and desktop widths | Navigation/forms remain usable | Not run | Not run |

Note: browser-based external CDN and OpenStreetMap features require internet access.
