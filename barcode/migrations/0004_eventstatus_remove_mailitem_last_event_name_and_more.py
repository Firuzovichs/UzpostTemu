# Generated by Django 5.1.7 on 2025-03-24 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('barcode', '0003_alter_mailitem_send_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='mailitem',
            name='last_event_name',
        ),
        migrations.AddField(
            model_name='mailitem',
            name='last_event_name',
            field=models.ManyToManyField(blank=True, to='barcode.eventstatus'),
        ),
    ]
