# Generated by Django 3.2.8 on 2021-12-02 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='last_use',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]