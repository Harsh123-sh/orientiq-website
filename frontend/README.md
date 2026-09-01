# ORENTIQ static frontend

This directory is the static public-site layer. It reuses the existing Django site's CSS, JavaScript, images, and visual language without changing the Django application.

Cloudflare Pages configuration:

- Framework preset: None / Static HTML
- Build command: empty
- Deploy command: empty
- Output directory: `frontend` when the repository root is selected, or `.` when this directory is the Pages root

The Django application remains the backend for authentication, admin, dashboard, forms, travel, bookings, and API operations. `js/site-config.js` contains only the public backend base URL; it contains no credentials.

Contact submission and authenticated workflows remain backend-dependent until dedicated cross-origin API/CSRF handling is provided by Django. The static public pages do not render through Django.
