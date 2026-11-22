import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from complaints.models import Complaint, ComplaintHistory, User

PW = "correct-horse-battery"
TMP_MEDIA = tempfile.mkdtemp(prefix="civicpulse-test-")

VALID = {
    "category": "Potholes and damaged roads", "title": "Large road pothole",
    "description": "A large pothole is creating a hazard near the bus stop.",
    "location": "Demo Road", "latitude": "12.97", "longitude": "77.59",
}


def png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buf, "PNG")
    return buf.getvalue()


@override_settings(MEDIA_ROOT=TMP_MEDIA,
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])  # fast tests only
class CivicPulseTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.admin = User.objects.create_superuser("admin@example.test", "Test Admin", PW)
        self.citizen = User.objects.create_user("citizen@example.test", "Test Citizen", PW)
        self.other = User.objects.create_user("other@example.test", "Other Citizen", PW)

    # ----- helpers
    def login(self, email="citizen@example.test"):
        return self.client.post(reverse("login"), {"email": email, "password": PW}, follow=True)

    def submit(self, **extra):
        data = {**VALID, **extra}
        return self.client.post(reverse("new_complaint"), data, follow=True)

    # ----- public pages / health
    def test_public_pages_load(self):
        for name in ("index", "login", "admin_login", "register", "track", "health"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_custom_404_page(self):
        r = self.client.get("/no/such/page/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "Page not found", status_code=404)

    # ----- registration / login
    def test_registration_and_duplicate_email(self):
        data = {"name": "New Person", "email": "new@example.test", "password": "password123"}
        first = self.client.post(reverse("register"), data, follow=True)
        self.assertContains(first, "Account created")
        self.client.post(reverse("logout"))
        second = self.client.post(reverse("register"), {**data, "email": "NEW@example.test"}, follow=True)
        self.assertContains(second, "already exists")

    def test_registration_validation(self):
        r = self.client.post(reverse("register"), {"name": "A", "email": "bad", "password": "short"}, follow=True)
        self.assertContains(r, "Name must be between 2 and 100 characters.")
        self.assertContains(r, "valid email")
        self.assertContains(r, "at least 8 characters")
        self.assertEqual(User.objects.filter(email="bad").count(), 0)

    def test_passwords_are_hashed(self):
        self.assertNotIn(PW, self.citizen.password)
        self.assertTrue(self.citizen.check_password(PW))

    def test_login_is_case_insensitive_and_protected_route(self):
        r = self.login("CITIZEN@Example.test")
        self.assertContains(r, "Citizen workspace")
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)

    def test_invalid_login(self):
        r = self.client.post(reverse("login"), {"email": "citizen@example.test", "password": "nope"}, follow=True)
        self.assertContains(r, "Invalid citizen email or password")

    def test_admin_cannot_use_citizen_login_and_vice_versa(self):
        r = self.client.post(reverse("login"), {"email": "admin@example.test", "password": PW}, follow=True)
        self.assertContains(r, "Invalid citizen email or password")
        r = self.client.post(reverse("admin_login"), {"email": "citizen@example.test", "password": PW}, follow=True)
        self.assertContains(r, "Invalid administrator email or password")

    def test_logout_requires_post(self):
        self.login()
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 302)

    def test_open_redirect_is_blocked(self):
        r = self.client.post(reverse("login") + "?next=https://evil.example/",
                             {"email": "citizen@example.test", "password": PW})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], reverse("dashboard"))

    # ----- access control
    def test_citizen_cannot_access_admin(self):
        self.login()
        for name in ("admin_dashboard", "admin_complaints", "analytics"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 403, name)

    def test_anonymous_admin_redirects_to_admin_login(self):
        r = self.client.get(reverse("admin_dashboard"))
        self.assertRedirects(r, reverse("admin_login"))

    # ----- complaints
    def test_complaint_submit_and_history(self):
        self.login()
        r = self.submit()
        self.assertContains(r, "Complaint submitted")
        c = Complaint.objects.get()
        self.assertEqual(c.latitude, 12.97)
        self.assertEqual(c.history.count(), 1)
        self.assertRegex(c.complaint_id, r"^CP-\d{4}-[0-9A-F]{6}$")

    def test_form_validation_messages(self):
        self.login()
        self.assertContains(self.submit(latitude="200", longitude="10"),
                            "Latitude must be -90 to 90 and longitude -180 to 180.")
        self.assertContains(self.submit(latitude="12", longitude=""), "Enter both latitude and longitude.")
        self.assertContains(self.submit(latitude="abc", longitude="1"), "Coordinates must be numbers.")
        self.assertContains(self.submit(category="Bogus"), "Choose a valid issue category.")
        self.assertContains(self.submit(description="short"), "Description must be between")
        self.assertEqual(Complaint.objects.count(), 0)

    def test_complaint_without_coordinates(self):
        self.login()
        self.submit(latitude="", longitude="")
        c = Complaint.objects.get()
        self.assertIsNone(c.latitude)
        self.assertFalse(c.has_coordinates)

    def test_citizen_sees_only_own_complaints(self):
        self.login()
        self.submit()
        c = Complaint.objects.get()
        self.assertContains(self.client.get(reverse("complaint_detail", args=[c.complaint_id])), c.title)
        self.client.post(reverse("logout"))
        self.login("other@example.test")
        self.assertEqual(self.client.get(reverse("complaint_detail", args=[c.complaint_id])).status_code, 403)
        self.assertNotContains(self.client.get(reverse("my_complaints")), c.complaint_id)

    def test_track_privacy(self):
        self.login()
        self.submit()
        c = Complaint.objects.get()
        self.client.post(reverse("logout"))
        r = self.client.post(reverse("track"), {"complaint_id": c.complaint_id.lower()}, follow=True)
        self.assertContains(r, "log in with the account")
        r = self.client.post(reverse("track"), {"complaint_id": "CP-0000-FFFFFF"}, follow=True)
        self.assertContains(r, "No complaint was found")

    # ----- photos
    def test_photo_upload_and_private_access(self):
        self.login()
        photo = SimpleUploadedFile("pothole.png", png_bytes(), content_type="image/png")
        self.submit(photo=photo)
        c = Complaint.objects.get()
        self.assertTrue(c.photo_name.endswith(".png"))
        url = reverse("uploaded_file", args=[c.photo_name])
        self.assertEqual(b"".join(self.client.get(url).streaming_content)[:4], b"\x89PNG")
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(url).status_code, 302)            # anonymous -> login
        self.login("other@example.test")
        self.assertEqual(self.client.get(url).status_code, 403)            # other citizen
        self.client.post(reverse("logout"))
        self.client.post(reverse("admin_login"), {"email": "admin@example.test", "password": PW})
        self.assertEqual(self.client.get(url).status_code, 200)            # admin

    def test_rejects_non_image_and_wrong_extension(self):
        self.login()
        bad = SimpleUploadedFile("evil.png", b"<?php echo 1; ?>", content_type="image/png")
        self.assertContains(self.submit(photo=bad), "Photo must be PNG, JPG, JPEG, or WEBP.")
        gif = io.BytesIO(); Image.new("RGB", (2, 2)).save(gif, "GIF")
        self.assertContains(self.submit(photo=SimpleUploadedFile("a.gif", gif.getvalue())),
                            "Photo must be PNG, JPG, JPEG, or WEBP.")
        self.assertEqual(Complaint.objects.count(), 0)

    @override_settings(MAX_UPLOAD_BYTES=10)
    def test_rejects_oversize_photo(self):
        self.login()
        r = self.submit(photo=SimpleUploadedFile("big.png", png_bytes(), content_type="image/png"))
        self.assertContains(r, "too large")

    # ----- admin workflow
    def test_admin_can_update_status_and_delete(self):
        self.login()
        self.submit()
        c = Complaint.objects.get()
        self.client.post(reverse("logout"))
        self.client.post(reverse("admin_login"), {"email": "admin@example.test", "password": PW})
        url = reverse("admin_complaint_detail", args=[c.complaint_id])
        self.assertEqual(self.client.get(url).status_code, 200)
        r = self.client.post(url, {"status": "In Progress", "priority": "High", "admin_note": "Crew assigned"}, follow=True)
        self.assertContains(r, "Complaint updated")
        c.refresh_from_db()
        self.assertEqual((c.status, c.priority), ("In Progress", "High"))
        self.assertEqual(c.history.count(), 2)
        self.assertContains(self.client.post(url, {"status": "Bogus", "priority": "High"}, follow=True),
                            "Invalid status or priority.")
        # wrong confirmation keeps it, correct confirmation deletes it
        d = reverse("delete_complaint", args=[c.complaint_id])
        self.client.post(d, {"confirm": "no"})
        self.assertEqual(Complaint.objects.count(), 1)
        self.client.post(d, {"confirm": "DELETE"})
        self.assertEqual(Complaint.objects.count(), 0)
        self.assertEqual(ComplaintHistory.objects.count(), 0)

    def test_admin_pages_render_with_data(self):
        self.login()
        self.submit()
        self.client.post(reverse("logout"))
        self.client.post(reverse("admin_login"), {"email": "admin@example.test", "password": PW})
        for name in ("admin_dashboard", "admin_complaints", "analytics", "complaint_map"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        r = self.client.get(reverse("admin_complaints"), {"q": "pothole", "status": "Submitted", "priority": "Normal",
                                                          "category": "Potholes and damaged roads"})
        self.assertContains(r, "Large road pothole")
        self.assertNotContains(self.client.get(reverse("admin_complaints"), {"q": "zzz"}), "Large road pothole")
        self.assertContains(self.client.get(reverse("analytics")), '"labels"')

    def test_map_shows_only_own_for_citizen_and_all_for_admin(self):
        self.login(); self.submit(); self.client.post(reverse("logout"))
        self.login("other@example.test")
        self.assertNotContains(self.client.get(reverse("complaint_map")), "CP-")
        self.client.post(reverse("logout"))
        self.client.post(reverse("admin_login"), {"email": "admin@example.test", "password": PW})
        self.assertContains(self.client.get(reverse("complaint_map")), "CP-")

    def test_profile_update(self):
        self.login()
        self.assertContains(self.client.post(reverse("profile"), {"name": "Renamed Person"}, follow=True), "Profile updated")
        self.citizen.refresh_from_db()
        self.assertEqual(self.citizen.name, "Renamed Person")
        self.assertContains(self.client.post(reverse("profile"), {"name": "x"}, follow=True), "Name must be between")

    def test_csrf_enforced(self):
        from django.test import Client
        c = Client(enforce_csrf_checks=True)
        r = c.post(reverse("login"), {"email": "citizen@example.test", "password": PW})
        self.assertEqual(r.status_code, 403)

    # ----- commands
    def test_management_commands(self):
        from django.core.management import call_command
        call_command("create_admin", email="boss@example.test", name="Boss", password="long-enough-pw")
        self.assertEqual(User.objects.get(email="boss@example.test").role, "admin")
        call_command("seed_demo")
        call_command("seed_demo")
        self.assertEqual(Complaint.objects.filter(title__startswith="[DEMO]").count(), 1)

    def test_django_admin_site_for_admin_role_only(self):
        self.assertEqual(self.client.get("/django-admin/").status_code, 302)
        self.client.force_login(self.citizen)
        self.assertEqual(self.client.get("/django-admin/").status_code, 302)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get("/django-admin/").status_code, 200)
