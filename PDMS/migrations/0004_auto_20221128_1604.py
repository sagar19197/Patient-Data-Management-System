# Generated by Django 3.2.16 on 2022-11-28 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PDMS', '0003_alter_organizations_desc'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizations',
            name='contact',
        ),
        migrations.AlterField(
            model_name='organizations',
            name='location',
            field=models.CharField(max_length=25),
        ),
    ]
