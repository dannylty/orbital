# Generated by Django 3.2.2 on 2021-06-03 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='name',
            field=models.CharField(blank=True, default='Anonymous', max_length=50),
        ),
    ]
