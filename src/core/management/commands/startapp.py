from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.startapp import Command as BaseCommand

class Command(BaseCommand):
    help = 'Create app local in folder'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='app name')

    def handle(self, *args, **options):
        directory = settings.BASE_DIR / 'src' / 'apps' / options['name']
        if directory.exists():
            raise CommandError('Is file had already been')

        directory.mkdir()
        directory.joinpath('__init__.py').touch()
        options.update(directory=str(directory))
        self.stdout.write(self.style.SUCCESS('Add folder!!!'))
