"""Manual-browser-style smoke test against a live runserver instance."""
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

BASE = "http://127.0.0.1:8055"
results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond), extra))
    print(f"{'PASS' if cond else 'FAIL'}: {name} {extra}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def build_opener():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(CookieJar()), NoRedirect()
    )


def get(path, opener):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "smoke"})
    return opener.open(req, timeout=30)


def post(path, data, opener, referer=None):
    body = urllib.parse.urlencode(data).encode("utf-8")
    headers = {"User-Agent": "smoke", "Content-Type": "application/x-www-form-urlencoded"}
    if referer:
        headers["Referer"] = BASE + referer
    req = urllib.request.Request(BASE + path, data=body, headers=headers)
    return opener.open(req, timeout=30)


def csrf_token(html):
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
    return m.group(1) if m else None
def main():
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orientiq.settings")
    import django

    django.setup()
    from django.contrib.auth.models import User
    from core.models import Profile, UserRole

    def ensure_user(username, email, password, role):
        u, created = User.objects.get_or_create(username=username, defaults={"email": email})
        if created:
            u.set_password(password)
            u.save()
        Profile.objects.get_or_create(user=u, defaults={"role": role})
        # Keep the intended password in sync for smoke runs.
        u.set_password(password)
        u.save()
        return u

    ensure_user("smokeclient", "smokeclient@example.com", "ClientPass123!", UserRole.CLIENT)
    ensure_user("smokeadmin", "smokeadmin@example.com", "AdminPass123!", UserRole.ADMIN)

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8055", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)
    try:
        _run_flow()
    finally:
        server.terminate()
        server.wait()

    failed = [x for x in results if not x[1]]
    print("\nSUMMARY:", len(results) - len(failed), "passed,", len(failed), "failed")
    sys.exit(1 if failed else 0)


def login(opener, username, password, path="/accounts/login/"):
    r = get(path, opener)
    html = r.read().decode("utf-8")
    token = csrf_token(html)
    resp = post(
        path,
        {"username": username, "password": password, "csrfmiddlewaretoken": token},
        opener,
        referer=path,
    )
    if resp.status != 302:
        try:
            body = resp.read().decode("utf-8", "ignore")
            import re as _re
            m = _re.search(r'class="_all_hidden"[^>]*>(.*?)</div>', body, _re.S)
            print("LOGIN STATUS", resp.status, "BODY SNIPPET:", body[:400])
        except Exception:
            pass
    return resp.status


def _run_flow():
    # ---- ANONYMOUS ----
    anon = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    r = get("/travel-search/", anon)
    html = r.read().decode("utf-8")
    check("anonymous travel-search renders", r.status == 200 and "Flights" in html)
    check("anonymous redirected from my-bookings", get("/accounts/bookings/", anon).status == 302)

    # ---- CLIENT full booking flow ----
    client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    status = login(client, "smokeclient", "ClientPass123!")
    check("client logs in", status == 302)

    qs = urllib.parse.urlencode({
        "item_type": "flight", "origin": "Ahmedabad", "destination": "Dubai",
        "departure": "2026-09-10", "trip_type": "one-way", "adults": "1",
        "cabin_class": "economy", "flight_number": "DA101",
    })
    r = get("/booking-review/?" + qs, client)
    html = r.read().decode("utf-8")
    check("booking review renders (200)", r.status == 200)
    check("review shows flight", "Demo Air" in html and "DA101" in html)
    check("review shows demo disclaimer", "DEMO RESERVATION" in html)
    check("review shows server price", "120.00" in html)
    token = csrf_token(html)
    check("review form has csrf", token is not None)

    data = {
        "item_type": "flight", "origin": "Ahmedabad", "destination": "Dubai",
        "departure": "2026-09-10", "trip_type": "one-way", "adults": "1",
        "cabin_class": "economy", "flight_number": "DA101",
        "person_0-first_name": "Smoke", "person_0-last_name": "Client",
        "person_0-email": "smokeclient@example.com", "person_0-phone": "9999999999",
        "person_0-nationality": "India",
        "price": "1", "total": "1",  # tamper attempts - must be ignored
        "csrfmiddlewaretoken": token,
    }
    r = post("/bookings/create/", data, client, referer="/booking-review/?" + qs)
    html = r.read().decode("utf-8")
    check("confirm returns redirect", r.status == 302)
    loc = r.headers.get("Location", "")
    check("redirect to confirmation page", "/confirmation/" in loc)
    m = re.search(r"ORI-[A-Z0-9]{8}", loc)
    ref = m.group(0) if m else "ORI-NONE"
    check("booking reference generated", m is not None)

    r = get(loc, client)
    html = r.read().decode("utf-8")
    check("confirmation page renders", r.status == 200 and "Booking Confirmed" in html)
    check("confirmation shows reference", ref in html)
    check("confirmation shows server total (not tampered)", "120.00" in html)

    r = get("/accounts/bookings/", client)
    html = r.read().decode("utf-8")
    check("my bookings lists booking", ref in html)

    r = get("/accounts/bookings/" + ref + "/", client)
    html = r.read().decode("utf-8")
    check("booking detail renders", r.status == 200 and "Demo Air" in html)

    r = get("/admin/bookings/", client)
    check("CLIENT denied admin bookings (403/302)", r.status in (302, 403))

    # ---- ADMIN ----
    admin = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    login(admin, "smokeadmin", "AdminPass123!", path="/admin/login/")
    r = get("/admin/bookings/", admin)
    check("admin booking list renders", r.status == 200)
    r = get("/admin/bookings/" + ref + "/", admin)
    check("admin booking detail renders", r.status == 200)


if __name__ == "__main__":
    main()