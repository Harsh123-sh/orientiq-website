from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
    ClientAccount,
    ClientDocument,
    ClientProject,
    Profile,
    UserRole,
)


class ClientPortalSecurityTests(TestCase):
    def setUp(self):
        self.one = User.objects.create_user("one", "one@example.com", "StrongPass123!")
        self.two = User.objects.create_user("two", "two@example.com", "StrongPass123!")
        Profile.objects.create(user=self.one, role=UserRole.CLIENT)
        Profile.objects.create(user=self.two, role=UserRole.CLIENT)
        self.account_one = ClientAccount.objects.create(user=self.one, status="active")
        self.account_two = ClientAccount.objects.create(user=self.two, status="active")
        self.project = ClientProject.objects.create(name="Private project", status="in_progress")
        self.project.clients.add(self.account_one)
        self.document = ClientDocument.objects.create(
            title="Private brief",
            category="requirements",
            client=self.account_one,
            project=self.project,
            uploaded_by=self.one,
            file=SimpleUploadedFile("brief.pdf", b"%PDF-1.4 private"),
        )

    def test_client_sees_only_assigned_data(self):
        self.client.login(username="one", password="StrongPass123!")
        response = self.client.get(reverse("client_dashboard"))
        self.assertContains(response, "Private project")
        self.assertContains(response, self.account_one.client_id)
        self.client.login(username="two", password="StrongPass123!")
        response = self.client.get(reverse("client_dashboard"))
        self.assertNotContains(response, "Private project")

    def test_client_cannot_download_another_clients_document(self):
        self.client.login(username="two", password="StrongPass123!")
        response = self.client.get(reverse("client_document_download", args=[self.document.pk]))
        self.assertEqual(response.status_code, 404)

    def test_suspended_client_cannot_open_portal_or_document(self):
        self.account_one.status = "suspended"
        self.account_one.save(update_fields=["status"])
        self.client.login(username="one", password="StrongPass123!")
        self.assertEqual(self.client.get(reverse("client_dashboard")).status_code, 302)
        self.assertEqual(
            self.client.get(reverse("client_document_download", args=[self.document.pk])).status_code,
            404,
        )


class LoginAccessControlTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "portal-admin", "admin@example.com", "StrongPass123!", is_staff=True
        )
        Profile.objects.create(user=self.admin, role=UserRole.ADMIN)
        self.client_user = User.objects.create_user(
            "portal-client", "client@example.com", "StrongPass123!"
        )
        Profile.objects.create(user=self.client_user, role=UserRole.CLIENT)
        ClientAccount.objects.create(user=self.client_user, status="active")

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(
            reverse("accounts_login"),
            {"username": "portal-admin", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("admin_dashboard"), fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 200)

    def test_admin_login_ignores_public_homepage_next_destination(self):
        response = self.client.post(
            f"{reverse('admin_login')}?next=/",
            {"username": "portal-admin", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("admin_dashboard"), fetch_redirect_response=False)

    def test_client_login_redirects_to_client_dashboard(self):
        response = self.client.post(
            reverse("accounts_login"),
            {"username": "portal-client", "password": "StrongPass123!"},
        )
        self.assertRedirects(response, reverse("client_dashboard"), fetch_redirect_response=False)

    def test_client_cannot_access_admin_management(self):
        self.client.login(username="portal-client", password="StrongPass123!")
        for route in (
            "admin_dashboard",
            "admin_client_list",
            "admin_project_list",
            "admin_document_list",
            "admin_inquiry_list",
        ):
            self.assertEqual(self.client.get(reverse(route)).status_code, 403)

    def test_logout_removes_client_dashboard_access(self):
        self.client.login(username="portal-client", password="StrongPass123!")
        self.client.get(reverse("accounts_logout"))
        response = self.client.get(reverse("client_dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('admin_login')}?next={reverse('client_dashboard')}",
            fetch_redirect_response=False,
        )

    def test_public_navigation_has_no_login_button(self):
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, 'href="/accounts/login/"')
        self.assertNotContains(response, ">Login<")

    def test_admin_authentication_does_not_change_public_navigation(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Admin Dashboard")
        self.assertNotContains(response, "Logout")
        self.assertContains(response, "Start a Project")
