import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Создает резервную копию базы данных PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Директория для сохранения бэкапов',
        )

    def handle(self, *args, **options):
        db_settings = settings.DATABASES['default']
        output_dir = options['output_dir']
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"library_backup_{timestamp}.sql"
        filepath = os.path.join(output_dir, filename)
        
        cmd = [
            'pg_dump',
            '-h', db_settings['HOST'],
            '-p', db_settings['PORT'],
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', filepath,
            '-w'  
        ]
        
        try:
            self.stdout.write(f'Создание резервной копии в {filepath}...')
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['PASSWORD']
            
            result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'Резервная копия успешно создана: {filepath}')
            )
            
            self.cleanup_old_backups(output_dir)
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании резервной копии: {e.stderr}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Неожиданная ошибка: {str(e)}')
            )


    def cleanup_old_backups(self, backup_dir, keep_count=10):
        """Удаляет старые бэкапы, оставляя только keep_count последних"""
        try:
            files = [f for f in os.listdir(backup_dir) if f.startswith('library_backup_') and f.endswith('.sql')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)))
            
            if len(files) > keep_count:
                for old_file in files[:-keep_count]:
                    os.remove(os.path.join(backup_dir, old_file))
                    self.stdout.write(f'Удален старый бэкап: {old_file}')
                    
        except Exception as e:
            self.stdout.write(f'Ошибка при очистке старых бэкапов: {str(e)}')