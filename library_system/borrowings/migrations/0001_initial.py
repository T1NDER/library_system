
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrowing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowed_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата выдачи')),
                ('due_date', models.DateTimeField(verbose_name='Срок возврата')),
                ('returned_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата возврата')),
                ('status', models.CharField(choices=[('active', 'Активна'), ('returned', 'Возвращена'), ('overdue', 'Просрочена')], default='active', max_length=10, verbose_name='Статус')),
                ('renew_count', models.IntegerField(default=0, verbose_name='Количество продлений')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book', verbose_name='Книга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Выдача книги',
                'verbose_name_plural': 'Выдачи книг',
                'ordering': ['-borrowed_date'],
            },
        ),
    ]
