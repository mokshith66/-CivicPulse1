import os
import secrets

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from .constants import (ROLE_ADMIN, ROLE_CHOICES, ROLE_CITIZEN, as_choices,
                        CATEGORIES, PRIORITIES, STATUSES)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, email):
        # Case-insensitive login: "A@x.com" and "a@x.com" are the same account.
        return self.get(email__iexact=email)

    def _create(self, email, name, password, **extra):
        if not email:
            raise ValueError("An email address is required.")
        user = self.model(email=self.normalize_email(email).lower(), name=name, **extra)
        user.set_password(password)  # stored as a salted PBKDF2 hash
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra):
        extra.setdefault("role", ROLE_CITIZEN)
        return self._create(email, name, password, **extra)

    def create_superuser(self, email, name, password=None, **extra):
        extra["role"] = ROLE_ADMIN
        extra["is_superuser"] = True
        return self._create(email, name, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CITIZEN)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    @property
    def is_admin_role(self):
        return self.role == ROLE_ADMIN

    @property
    def is_staff(self):
        # Administrators may also open the built-in Django admin site.
        return self.role == ROLE_ADMIN

    @property
    def short_name(self):
        return self.name.split(" ")[0] if self.name else ""


def complaint_photo_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"{secrets.token_hex(12)}{ext}"


def make_complaint_id():
    """CP-<year>-<6 hex>. The unique constraint is the final safeguard."""
    while True:
        candidate = f"CP-{timezone.now().year}-{secrets.token_hex(3).upper()}"
        if not Complaint.objects.filter(complaint_id=candidate).exists():
            return candidate


class Complaint(models.Model):
    complaint_id = models.CharField(max_length=30, unique=True, default=make_complaint_id, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    category = models.CharField(max_length=80, choices=as_choices(CATEGORIES), db_index=True)
    title = models.CharField(max_length=140)
    description = models.TextField()
    location = models.CharField(max_length=240)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to=complaint_photo_path, blank=True)
    status = models.CharField(max_length=30, choices=as_choices(STATUSES), default="Submitted", db_index=True)
    priority = models.CharField(max_length=20, choices=as_choices(PRIORITIES), default="Normal", db_index=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.complaint_id} – {self.title}"

    @property
    def photo_name(self):
        return os.path.basename(self.photo.name) if self.photo else ""

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="history")
    previous_status = models.CharField(max_length=30, blank=True, null=True)
    new_status = models.CharField(max_length=30)
    note = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["changed_at", "id"]
        verbose_name_plural = "complaint history"

    @property
    def actor(self):
        return self.changed_by

    def __str__(self):
        return f"{self.complaint.complaint_id}: {self.previous_status or 'Created'} → {self.new_status}"
