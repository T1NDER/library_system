
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'Вход в систему'), ('logout', 'Выход из системы'), ('borrow', 'Выдача книги'), ('return', 'Возврат книги'), ('add_book', 'Добавление книги'), ('edit_book', 'Редактирование книги'), ('delete_book', 'Удаление книги'), ('add_user', 'Добавление пользователя'), ('edit_user', 'Редактирование пользователя'), ('view_report', 'Просмотр отчета')], max_length=20)),
                ('description', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['-timestamp'], name='core_auditl_timesta_189a84_idx'), models.Index(fields=['action'], name='core_auditl_action_d9fb24_idx'), models.Index(fields=['user'], name='core_auditl_user_id_2ff9b7_idx')],
            },
        ),
    ]
