# Generated by Django 3.2 on 2022-04-01 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0019_auto_20220130_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingordersmodel',
            name='billing_date',
            field=models.DateTimeField(default=None),
        ),
    ]
