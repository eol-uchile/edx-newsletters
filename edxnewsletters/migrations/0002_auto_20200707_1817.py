# Generated by Django 2.2.13 on 2020-07-07 18:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('edxnewsletters', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EdxNewslettersUnsuscribed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='EdxNewslettersSuscribed',
        ),
    ]
