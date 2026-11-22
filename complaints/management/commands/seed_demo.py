import secrets

from django.core.management.base import BaseCommand

from complaints.models import Complaint, ComplaintHistory, User


class Command(BaseCommand):
    help = "Add a clearly labelled sample citizen and complaint for demonstrations."

    def handle(self, *args, **opts):
        email = "demo.citizen@example.test"
        if User.objects.filter(email=email).exists():
            self.stdout.write("Demo citizen already exists.")
            return
        citizen = User.objects.create_user(email=email, name="Demo Citizen (sample)",
                                           password=secrets.token_urlsafe(16))
        sample = Complaint.objects.create(
            user=citizen, category="Potholes and damaged roads", title="[DEMO] Sample pothole",
            description="This is sample data for a local demonstration only.",
            location="Demo location, Bengaluru", latitude=12.9716, longitude=77.5946)
        ComplaintHistory.objects.create(complaint=sample, previous_status=None, new_status="Submitted",
                                        note="Sample demo record.", changed_by=citizen)
        self.stdout.write("Sample record created. Demo citizen password is intentionally not printed.")
