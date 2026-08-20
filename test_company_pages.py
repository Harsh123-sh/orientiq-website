#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orientiq.settings')
django.setup()

from django.test import Client

client = Client(HTTP_HOST="127.0.0.1")

company_routes = [
    ("/company/", "Company Landing"),
    ("/company/about/", "About"),
    ("/company/process/", "Process"),
    ("/company/careers/", "Careers"),
    ("/company/contact/", "Contact"),
]

print("Testing Company Pages:")
print("=" * 60)

all_pass = True
for route, name in company_routes:
    resp = client.get(route)
    status = "✓" if resp.status_code == 200 else "✗"
    if resp.status_code != 200:
        all_pass = False
    print(f"{status} {name:<20} {route:<25} {resp.status_code}")

print("=" * 60)
if all_pass:
    print("✓ All Company pages return 200")
else:
    print("✗ Some pages failed")

# Check for problematic content in careers page
print("\nVerifying Careers page content:")
print("-" * 60)

careers_resp = client.get("/company/careers/")
careers_content = careers_resp.content.decode()

# Should NOT contain fake job listings
bad_phrases = [
    "Senior Django Developer",
    "AI / ML Engineer", 
    "Product Designer",
    "DevOps Engineer",
    "Open Roles",
    "Current opportunities",
]

found_bad_phrases = []
for phrase in bad_phrases:
    if phrase in careers_content:
        found_bad_phrases.append(phrase)

# SHOULD contain new content
good_phrases = [
    "Future Opportunities",
    "Areas we may hire for as we grow",
    "Growing with us",
    "Build what's next with ORENTIQ",
]

found_good_phrases = []
for phrase in good_phrases:
    if phrase in careers_content:
        found_good_phrases.append(phrase)

if found_bad_phrases:
    print(f"✗ Found old job listings: {', '.join(found_bad_phrases)}")
    all_pass = False
else:
    print("✓ No old job listings found")

for phrase in good_phrases:
    status = "✓" if phrase in careers_content else "✗"
    print(f"{status} '{phrase}' present")

print("\nVerifying Process page content:")
print("-" * 60)

process_resp = client.get("/company/process/")
process_content = process_resp.content.decode()

# Should NOT contain unsupported claims
bad_process = [
    "zero downtime",
    "0 Downtime",
    "100% Transparent",
    "Senior team on every engagement",
]

found_bad_process = []
for phrase in bad_process:
    if phrase in process_content:
        found_bad_process.append(phrase)

if found_bad_process:
    print(f"✗ Found unsupported claims: {', '.join(found_bad_process)}")
    all_pass = False
else:
    print("✓ No unsupported claims found")

# SHOULD contain qualified language
good_process = [
    "Experienced team focused on your success",
    "carefully with rigorous testing",
]

for phrase in good_process:
    status = "✓" if phrase in process_content else "✗"
    print(f"{status} '{phrase}' present")

print("\n" + "=" * 60)
if all_pass:
    print("✓✓✓ All verifications passed!")
else:
    print("✗✗✗ Some verifications failed")
