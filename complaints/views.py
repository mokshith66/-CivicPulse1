import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .constants import CATEGORIES, PRIORITIES, ROLE_ADMIN, ROLE_CITIZEN, STATUSES
from .decorators import admin_required, login_required
from .forms import AdminUpdateForm, ComplaintForm, ProfileForm, RegisterForm
from .models import Complaint, ComplaintHistory, User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------- helpers
def flash_form_errors(request, form):
    for errors in form.errors.values():
        for error in errors:
            messages.error(request, error)


def can_view(user, complaint):
    return user.role == ROLE_ADMIN or complaint.user_id == user.id


def safe_next(request):
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                                  require_https=request.is_secure()):
        return target
    return ""


# ----------------------------------------------------------------- public
def index(request):
    counts = {
        "total": Complaint.objects.count(),
        "resolved": Complaint.objects.filter(status="Resolved").count(),
        "categories": len(CATEGORIES),
    }
    return render(request, "index.html", {"counts": counts})


def health(request):
    """Used by load balancers / quick checks: GET /health/ -> 200 ok."""
    from django.http import HttpResponse
    return HttpResponse("ok", content_type="text/plain")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data["email"], name=form.cleaned_data["name"],
                password=form.cleaned_data["password"], role=ROLE_CITIZEN)
            login(request, user)
            messages.success(request, "Account created. Welcome to CivicPulse!")
            return redirect("dashboard")
        flash_form_errors(request, form)
    return render(request, "auth/register.html")


def _do_login(request, admin):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        wanted = ROLE_ADMIN if admin else ROLE_CITIZEN
        if user is not None and user.role == wanted:
            login(request, user)
            if admin:
                messages.success(request, "Administrator login successful.")
                return redirect("admin_dashboard")
            messages.success(request, "You are now logged in.")
            return redirect(safe_next(request) or "dashboard")
        messages.error(request, "Invalid administrator email or password." if admin
                       else "Invalid citizen email or password.")
    return render(request, "auth/login.html", {"admin": admin, "next": safe_next(request)})


def login_view(request):
    return _do_login(request, admin=False)


def admin_login(request):
    return _do_login(request, admin=True)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("index")


# ----------------------------------------------------------------- citizen
@login_required
def dashboard(request):
    mine = Complaint.objects.filter(user=request.user)
    return render(request, "citizen/dashboard.html",
                  {"complaints": mine.order_by("-created_at")[:5], "total": mine.count()})


@login_required
def new_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            complaint = Complaint.objects.create(
                user=request.user, category=data["category"], title=data["title"],
                description=data["description"], location=data["location"],
                latitude=data["latitude"], longitude=data["longitude"],
                photo=data["photo"] or "", status="Submitted", priority="Normal")
            ComplaintHistory.objects.create(
                complaint=complaint, previous_status=None, new_status="Submitted",
                note="Complaint submitted by citizen.", changed_by=request.user)
            messages.success(request, f"Complaint submitted. Your ID is {complaint.complaint_id}.")
            return redirect("complaint_detail", complaint_id=complaint.complaint_id)
        flash_form_errors(request, form)
        return render(request, "citizen/new_complaint.html", {"form": request.POST})
    return render(request, "citizen/new_complaint.html", {"form": {}})


@login_required
def my_complaints(request):
    qs = Complaint.objects.filter(user=request.user)
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if search:
        qs = qs.filter(Q(complaint_id__icontains=search) | Q(title__icontains=search))
    if status in STATUSES:
        qs = qs.filter(status=status)
    return render(request, "citizen/complaints.html",
                  {"complaints": qs.order_by("-created_at"), "search": search, "selected_status": status})


def track(request):
    complaint_id = (request.POST.get("complaint_id") or request.GET.get("complaint_id") or "").strip().upper()
    if request.method == "POST" and complaint_id:
        complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
        if not complaint:
            messages.warning(request, "No complaint was found with that ID.")
        elif not request.user.is_authenticated or not can_view(request.user, complaint):
            messages.warning(request, "For privacy, log in with the account that submitted this complaint.")
        else:
            return redirect("complaint_detail", complaint_id=complaint.complaint_id)
    return render(request, "track.html", {"complaint_id": complaint_id})


@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint.objects.select_related("user"), complaint_id=complaint_id)
    if not can_view(request.user, complaint):
        raise PermissionDenied
    history = complaint.history.select_related("changed_by")
    point = {"lat": complaint.latitude, "lon": complaint.longitude, "id": complaint.complaint_id} \
        if complaint.has_coordinates else None
    return render(request, "citizen/complaint_detail.html",
                  {"complaint": complaint, "history": history, "point": point})


@login_required
def uploaded_file(request, filename):
    """Photos are private: only the owner or an administrator may fetch them."""
    complaint = Complaint.objects.filter(photo=filename).first()
    if not complaint or not complaint.photo:
        raise Http404
    if not can_view(request.user, complaint):
        raise PermissionDenied
    try:
        return FileResponse(complaint.photo.open("rb"))
    except FileNotFoundError:
        raise Http404


@login_required
def complaint_map(request):
    qs = Complaint.objects.filter(latitude__isnull=False, longitude__isnull=False)
    if request.user.role != ROLE_ADMIN:
        qs = qs.filter(user=request.user)
    markers = [{"id": c.complaint_id, "category": c.category, "status": c.status,
                "location": c.location, "lat": c.latitude, "lon": c.longitude,
                "url": reverse("complaint_detail", kwargs={"complaint_id": c.complaint_id})}
               for c in qs]
    return render(request, "map.html", {"markers": markers})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            request.user.name = form.cleaned_data["name"]
            request.user.save(update_fields=["name"])
            messages.success(request, "Profile updated.")
            return redirect("profile")
        flash_form_errors(request, form)
    return render(request, "profile.html")


# ------------------------------------------------------------------- admin
@admin_required
def admin_dashboard(request):
    by_status = dict(Complaint.objects.values_list("status").annotate(n=Count("id")))
    total = Complaint.objects.count()
    cards = [("Total", total, "clipboard-data"),
             ("Submitted", by_status.get("Submitted", 0), "inbox"),
             ("Acknowledged", by_status.get("Acknowledged", 0), "eye"),
             ("In progress", by_status.get("In Progress", 0), "gear"),
             ("Resolved", by_status.get("Resolved", 0), "check-circle"),
             ("Rejected", by_status.get("Rejected", 0), "x-circle")]
    recent = Complaint.objects.select_related("user").order_by("-created_at")[:8]
    return render(request, "admin_panel/dashboard.html", {"cards": cards, "recent": recent})


@admin_required
def admin_complaints(request):
    qs = Complaint.objects.select_related("user")
    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    if search:
        qs = qs.filter(Q(complaint_id__icontains=search) | Q(title__icontains=search)
                       | Q(user__email__icontains=search))
    if category in CATEGORIES:
        qs = qs.filter(category=category)
    if status in STATUSES:
        qs = qs.filter(status=status)
    if priority in PRIORITIES:
        qs = qs.filter(priority=priority)
    return render(request, "admin_panel/complaints.html", {
        "complaints": qs.order_by("-created_at"), "search": search,
        "selected_category": category, "selected_status": status, "selected_priority": priority})


@admin_required
def admin_complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint.objects.select_related("user"), complaint_id=complaint_id)
    if request.method == "POST":
        form = AdminUpdateForm(request.POST)
        if form.is_valid():
            old_status = complaint.status
            note = form.cleaned_data["admin_note"]
            complaint.status = form.cleaned_data["status"]
            complaint.priority = form.cleaned_data["priority"]
            complaint.admin_note = note
            complaint.save()
            if old_status != complaint.status or note:
                ComplaintHistory.objects.create(
                    complaint=complaint, previous_status=old_status, new_status=complaint.status,
                    note=note or None, changed_by=request.user)
            messages.success(request, "Complaint updated.")
            return redirect("admin_complaint_detail", complaint_id=complaint.complaint_id)
        flash_form_errors(request, form)
    return render(request, "admin_panel/complaint_detail.html",
                  {"complaint": complaint, "history": complaint.history.select_related("changed_by")})


@admin_required
@require_POST
def delete_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.POST.get("confirm") != "DELETE":
        messages.error(request, "Deletion not confirmed.")
    else:
        if complaint.photo:
            complaint.photo.delete(save=False)
        complaint.delete()
        messages.info(request, "Test complaint deleted.")
    return redirect("admin_complaints")


@admin_required
def analytics(request):
    cats = Complaint.objects.values_list("category").annotate(n=Count("id")).order_by("category")
    stats = Complaint.objects.values_list("status").annotate(n=Count("id")).order_by("status")
    dates = (Complaint.objects.annotate(day=TruncDate("created_at"))
             .values_list("day").annotate(n=Count("id")).order_by("day"))
    chart = {
        "category": {"labels": [r[0] for r in cats], "values": [r[1] for r in cats]},
        "status": {"labels": [r[0] for r in stats], "values": [r[1] for r in stats]},
        "time": {"labels": [str(r[0]) for r in dates], "values": [r[1] for r in dates]},
    }
    return render(request, "admin_panel/analytics.html", {"chart": chart})


# ------------------------------------------------------------ error pages
def forbidden(request, exception=None):
    return render(request, "403.html", status=403)


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    logger.error("Unhandled server error on %s", request.path)
    return render(request, "500.html", status=500)
