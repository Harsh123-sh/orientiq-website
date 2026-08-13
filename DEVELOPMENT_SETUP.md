# Orientiq Development Setup — Gmail SMTP Email

This guide explains how to enable real password-reset emails via Gmail SMTP.

---

## 1. Enable Google 2-Step Verification

1. Go to https://myaccount.google.com/security
2. Sign in with **the dedicated Orientiq Gmail account** (do not use your personal Gmail).
3. Under **"How you sign in to Google"**, click **2-Step Verification**.
4. Follow the prompts to enable it.

## 2. Create a Google App Password

App Passwords allow third-party apps to send email via Gmail **without using your normal password**.

1. Go to https://myaccount.google.com/apppasswords
   - (If the link is not visible, use: https://myaccount.google.com/security → App passwords)
2. Confirm 2-Step Verification is enabled.
3. Under "App name", enter something like `Orientiq Django`.
4. Click **Create**.
5. Google shows a 16-character password, e.g. `abcd efgh ijkl mnop`.
   - Copy it **now** — it is only shown once.
6. **Never share or commit this password.**

## 3. Environment Variables (.env)

Create a `.env` file in the project root with the following values.

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=the-orientiq-gmail@gmail.com
EMAIL_HOST_PASSWORD=the-google-app-password
DEFAULT_FROM_EMAIL=the-orientiq-gmail@gmail.com
```

- The **App Password** goes in `EMAIL_HOST_PASSWORD` (with or without spaces — Google accepts both).
- `.env` is already listed in `.gitignore`, so it will never be committed.
- `.env.example` contains placeholders for reference only.

> **Security**: Never put real credentials in `settings.py`, templates, JavaScript, or any Git-tracked file.

## 4. How Settings Detect SMTP

`orientiq/settings.py` checks:

- If `EMAIL_HOST` is set → uses the SMTP backend (`smtp.EmailBackend`).
- If `EMAIL_HOST` is empty → uses the console backend (prints emails to the terminal — useful for local development without SMTP).

## 5. How to Test Email Sending

### Option A — Real Gmail (recommended for manual test)

1. Start the server: `python manage.py runserver 8000`
2. Open http://127.0.0.1:8000/accounts/login/
3. Click **Forgot Password?**
4. Enter a registered email address and submit.
5. Check the recipient's real Gmail inbox — you should receive the reset email.

### Option B — Console (no SMTP needed)

1. Ensure `EMAIL_HOST` is **not** set in the environment.
2. Submit the forgot-password form.
3. The email appears in the terminal (not delivered to a real inbox).

## 6. Troubleshooting SMTP Authentication Errors

| Error | Likely cause | Fix |
|---|---|---|
| `SMTPAuthenticationError: 535, 5.7.8 Username and Password not accepted` | Wrong App Password or normal password used | Recreate the App Password and remove spaces |
| `SMTPAuthenticationError: 534, 5.7.9 Application-specific password required` | 2-Step Verification not enabled | Enable 2-Step Verification first |
| `ConnectionRefusedError` | No EMAIL_HOST configured / using console fallback | Set `EMAIL_HOST=smtp.gmail.com` in `.env` |
| `HELO/EHLO` timeout | Network/firewall blocking port 587 | Use a network that allows outbound SMTP on 587 |

## 7. Files

- `orientiq/settings.py` — environment-based email configuration
- `.env.example` — placeholder template (no real credentials)
- `.gitignore` — excludes `.env` (line 17)