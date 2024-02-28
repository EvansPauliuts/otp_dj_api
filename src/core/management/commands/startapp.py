from django.conf import settings
from django.core.management.commands.startapp import Command as BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        directory = settings.BASE_DIR / 'apps' / options['name']
        directory.mkdir(exist_ok=True)
        options.update(directory=str(directory))

        super().handle(**options)
