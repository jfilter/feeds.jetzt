# Generated by Django 2.1.2 on 2018-10-11 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20181011_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='description',
            field=models.TextField(),
        ),
    ]
