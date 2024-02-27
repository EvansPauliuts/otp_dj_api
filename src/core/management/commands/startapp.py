from django.conf import settings
from django.core.management.commands.startapp import Command as BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        dir = settings.BASE_DIR.parent / 'apps' / options['name']
        dir.mkdir(exist_ok=True)
        options.update(directory=str(dir))

        super().handle(**options)
