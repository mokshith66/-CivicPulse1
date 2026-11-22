import getpass
import re

from django.core.management.base import BaseCommand

from complaints.models import User

EMAIL_RE = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")


class Command(BaseCommand):
    help = ("Create a CivicPulse administrator. Run with no arguments for an interactive prompt "
            "(no default password is ever provided), or pass --email/--name/--password for scripts.")

    def add_arguments(self, parser):
        parser.add_argument("--email")
        parser.add_argument("--name")
        parser.add_argument("--password")

    def handle(self, *args, **opts):
        email = (opts["email"] or input("Administrator email: ")).strip().lower()
        name = (opts["name"] or input("Administrator name: ")).strip()
        password = opts["password"] or getpass.getpass("Choose administrator password (8+ chars): ")
        if len(name) < 2 or len(password) < 8 or not EMAIL_RE.fullmatch(email):
            self.stderr.write(self.style.ERROR("Invalid name/email/password."))
            return
        if User.objects.filter(email__iexact=email).exists():
            self.stderr.write(self.style.ERROR("That email already exists."))
            return
        User.objects.create_superuser(email=email, name=name, password=password)
        self.stdout.write(self.style.SUCCESS("Administrator created."))
