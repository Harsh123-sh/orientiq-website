import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orientiq.settings")
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Profile, UserRole

u, created = User.objects.get_or_create(username="smokeclient", defaults={"email": "smokeclient@example.com"})
if created:
    u.set_password("ClientPass123!")
    u.save()
Profile.objects.get_or_create(user=u, defaults={"role": UserRole.CLIENT})
u.refresh_from_db()
print("USER", u.username, "ACTIVE", u.is_active)

c = Client(HTTP_HOST="127.0.0.1")
r = c.get("/accounts/login/")
print("LOGIN GET", r.status_code)
ok = c.login(username="smokeclient", password="ClientPass123!")
print("CLIENT.login() =>", ok)

r = c.get("/booking-review/", {
    "item_type": "flight", "origin": "Ahmedabad", "destination": "Dubai",
    "departure": "2026-09-10", "trip_type": "one-way", "adults": "1",
    "cabin_class": "economy", "flight_number": "DA101",
})
print("REVIEW AS CLIENT", r.status_code)