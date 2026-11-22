from django import forms
from django.core.validators import FileExtensionValidator
from django.conf import settings

from .constants import ALLOWED_EXTENSIONS, CATEGORIES, PRIORITIES, STATUSES, as_choices
from .models import User


class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=100, strip=True,
        error_messages={"required": "Name must be between 2 and 100 characters.",
                        "max_length": "Name must be between 2 and 100 characters."})
    email = forms.EmailField(
        error_messages={"required": "Enter a valid email address.",
                        "invalid": "Enter a valid email address."})
    password = forms.CharField(
        strip=False,
        error_messages={"required": "Password must contain at least 8 characters."})

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("Name must be between 2 and 100 characters.")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with that email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("Password must contain at least 8 characters.")
        return password


class ProfileForm(forms.Form):
    name = forms.CharField(
        max_length=100, strip=True,
        error_messages={"required": "Name must be between 2 and 100 characters.",
                        "max_length": "Name must be between 2 and 100 characters."})

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("Name must be between 2 and 100 characters.")
        return name


class ComplaintForm(forms.Form):
    category = forms.ChoiceField(
        choices=as_choices(CATEGORIES),
        error_messages={"required": "Choose a valid issue category.",
                        "invalid_choice": "Choose a valid issue category."})
    title = forms.CharField(
        max_length=140, strip=True,
        error_messages={"required": "Title is required and must be 140 characters or fewer.",
                        "max_length": "Title is required and must be 140 characters or fewer."})
    description = forms.CharField(
        min_length=10, max_length=5000, strip=True,
        error_messages={"required": "Description must be between 10 and 5,000 characters.",
                        "min_length": "Description must be between 10 and 5,000 characters.",
                        "max_length": "Description must be between 10 and 5,000 characters."})
    location = forms.CharField(
        max_length=240, strip=True,
        error_messages={"required": "Enter a location (maximum 240 characters).",
                        "max_length": "Enter a location (maximum 240 characters)."})
    latitude = forms.CharField(required=False, strip=True)
    longitude = forms.CharField(required=False, strip=True)
    photo = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(ALLOWED_EXTENSIONS, message="Photo must be PNG, JPG, JPEG, or WEBP.")],
        error_messages={"invalid_image": "Photo must be PNG, JPG, JPEG, or WEBP.",
                        "invalid": "Photo must be PNG, JPG, JPEG, or WEBP."})

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > settings.MAX_UPLOAD_BYTES:
            raise forms.ValidationError(
                f"Photo is too large. Maximum size is {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")
        return photo

    def clean(self):
        cleaned = super().clean()
        lat_raw = (cleaned.get("latitude") or "").strip()
        lon_raw = (cleaned.get("longitude") or "").strip()
        cleaned["latitude"] = cleaned["longitude"] = None
        if not lat_raw and not lon_raw:
            return cleaned
        if not lat_raw or not lon_raw:
            raise forms.ValidationError("Enter both latitude and longitude.")
        try:
            lat, lon = float(lat_raw), float(lon_raw)
        except ValueError:
            raise forms.ValidationError("Coordinates must be numbers.")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise forms.ValidationError("Latitude must be -90 to 90 and longitude -180 to 180.")
        cleaned["latitude"], cleaned["longitude"] = lat, lon
        return cleaned


class AdminUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=as_choices(STATUSES),
                               error_messages={"invalid_choice": "Invalid status or priority.",
                                               "required": "Invalid status or priority."})
    priority = forms.ChoiceField(choices=as_choices(PRIORITIES),
                                 error_messages={"invalid_choice": "Invalid status or priority.",
                                                 "required": "Invalid status or priority."})
    admin_note = forms.CharField(required=False, strip=True)

    def clean_admin_note(self):
        return (self.cleaned_data.get("admin_note") or "")[:3000]
