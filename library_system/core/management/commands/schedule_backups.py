import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

class Command(BaseCommand):
    help = 'Запускает планировщик для автоматического резервного копирования'

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        
        scheduler.add_job(
            self.run_backup,
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_backup',
            name='Ежедневное резервное копирование БД',
            replace_existing=True
        )
        
        try:
            scheduler.start()
            self.stdout.write(self.style.SUCCESS('Планировщик резервного копирования запущен'))
         
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Планировщик резервного копирования остановлен'))

    def run_backup(self):
        """Выполняет команду резервного копирования"""
        call_command('backup_db')