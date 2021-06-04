# Generated by Django 3.2.2 on 2021-06-04 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20210604_2003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='faculty',
            field=models.CharField(choices=[('anon', 'Anonymous'), ('sci', 'Science'), ('com', 'Computing'), ('law', 'Law'), ('biz', 'Business'), ('wtv', 'Wtv')], default='anon', max_length=10),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='year',
            field=models.CharField(choices=[('anon', 'Anonymous'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], default='anon', max_length=10),
        ),
    ]
