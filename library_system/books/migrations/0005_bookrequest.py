
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_alter_book_isbn'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BookRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Ожидает рассмотрения'), ('approved', 'Одобрена'), ('rejected', 'Отклонена')], default='pending', max_length=10, verbose_name='Статус')),
                ('requested_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')),
                ('approved_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата одобрения')),
                ('rejected_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата отклонения')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Примечания')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book', verbose_name='Книга')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заявка на книгу',
                'verbose_name_plural': 'Заявки на книги',
                'ordering': ['-requested_date'],
                'unique_together': {('user', 'book', 'status')},
            },
        ),
    ]
