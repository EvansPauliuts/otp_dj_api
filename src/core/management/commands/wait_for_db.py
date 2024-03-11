import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        delay = 1

        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write(
                    self.style.WARNING(
                        f'Database unavailable, waiting {delay} second(s)...',
                    ),
                )
                time.sleep(delay)
                delay = min(60, delay * 2)

        self.stdout.write(self.style.SUCCESS('Database available!'))
