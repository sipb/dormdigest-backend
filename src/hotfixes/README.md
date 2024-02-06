# Hotfixes

This directory contains code for hotfixes we had to do for the dormdigest backend. They are preserved here in case we may need to reuse tools/code here again.

Directory:

- **06-17-23_MIME_Encoded**
  - **Issue:** Event emails stored in the database were in MIME quoted-printable data form, and needs to be decoded for proper display on the dormdigest frontend.
- **02-05-2023_Sent_Date_UTC**
  - **Issue:** Event email sent time stored in the database as `.date_created` attribute are in `ISO_LOCAL_DATE_TIME` (e.g., `2024-02-01T23:09:54`), but they are actually in UTC. This causes the frontend to show the UTC time when in "Sent dates" view mode
  - **Fix:** For future emails, we will automatically tack on the "Z" identifier for UTC time. We also go through all previous events and revise the `.date_created` attribute 