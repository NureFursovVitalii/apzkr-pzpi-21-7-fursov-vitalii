import os
from django.core.management.base import BaseCommand
from django.conf import settings
import datetime

class Command(BaseCommand):
    help = 'Backup the PostgreSQL database'

    def handle(self, *args, **kwargs):
        # Backup database
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        date_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        db_backup_file = os.path.join(backup_dir, f'{db_name}_backup_{date_str}.sql')

        os.environ['PGPASSWORD'] = db_password
        pg_dump_path = '/Library/PostgreSQL/16/bin/pg_dump'  
        dump_cmd = f'{pg_dump_path} -U {db_user} -h {db_host} -p {db_port} {db_name} > {db_backup_file}'
        os.system(dump_cmd)

        self.stdout.write(self.style.SUCCESS(f'Successfully backed up the database to {db_backup_file}'))
