from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser for the admin panel'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Username')
        parser.add_argument('--email', default='admin@example.com', help='Email')
        parser.add_argument('--password', default='admin123', help='Password')

    def handle(self, *args, **options):
        if not User.objects.filter(username=options['username']).exists():
            User.objects.create_superuser(
                options['username'], options['email'], options['password']
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{options['username']}' created successfully."))
        else:
            self.stdout.write(f"Superuser '{options['username']}' already exists.")
