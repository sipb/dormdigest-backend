# Hotfixes

This directory contains code for hotfixes we had to do for the dormdigest backend. They are preserved here in case we may need to reuse tools/code here again.

Directory:

- **06-17-23_MIME_Encoded**
  - **Issue:** Event emails stored in the database were in MIME quoted-printable data form, and needs to be decoded for proper display on the dormdigest frontend.
- **02-05-2024_Sent_Date_UTC**
  - **Issue:** Event email sent time stored in the database as `.date_created` attribute are in `ISO_LOCAL_DATE_TIME` (e.g., `2024-02-01T23:09:54`), but they are actually in UTC. This causes the frontend to show the UTC time when in "Sent dates" view mode
  - **Fix:** For future emails, we will automatically convert the UTC time timestamps to EST. We also go through all previous events and revise the `.date_created` attribute accordingly.
- **04-10-2024_Missing_Events**
  - **Issue:** It came to our attention that events from March 19th to April 10th were not sent to the production Python backend, though they were properly processed by the XVM Python backend instance. Since it'll be too much effort to try to port over the events + event descriptions + user tables, we've decided to just port over the Session IDs from the production database into the XVM database, and to use the XVM database as the new production copy.