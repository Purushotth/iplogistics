# Generated by Django 3.2 on 2021-12-19 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0008_auto_20211219_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='truckmodel',
            name='mileage',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
