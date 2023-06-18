# Hotfixes

This directory contains code for hotfixes we had to do for the dormdigest backend. They are preserved here in case we may need to reuse tools/code here again.

Directory:

- **06-17-23_MIME_Encoded**
  - **Issue:** Event emails stored in the database were in MIME quoted-printable data form, and needs to be decoded for proper display on the dormdigest frontend.