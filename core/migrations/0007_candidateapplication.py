# Generated manually because the local Python environment is unavailable.

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_alter_sitesetting_company_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="CandidateApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("area_of_interest", models.CharField(choices=[("ai_ml", "AI & Machine Learning"), ("web", "Web Development"), ("software", "Software Development"), ("mobile", "Mobile Development"), ("design", "UI/UX Design"), ("cloud", "Cloud & DevOps"), ("business", "Business & Operations"), ("other", "Other")], max_length=20)),
                ("experience_level", models.CharField(choices=[("student", "Student / Fresher"), ("entry", "Entry Level"), ("one_to_three", "1–3 Years"), ("three_to_five", "3–5 Years"), ("five_plus", "5+ Years")], max_length=20)),
                ("portfolio_url", models.URLField(blank=True)),
                ("github_url", models.URLField(blank=True)),
                ("resume", models.FileField(blank=True, upload_to=core.models.candidate_resume_upload_to)),
                ("introduction", models.TextField(max_length=1500)),
                ("consented_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("new", "New"), ("under_review", "Under Review"), ("shortlisted", "Shortlisted"), ("archived", "Archived"), ("rejected", "Rejected")], default="new", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Candidate application", "verbose_name_plural": "Candidate applications", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="candidateapplication",
            index=models.Index(fields=["status", "-created_at"], name="candidate_status_date_idx"),
        ),
    ]
