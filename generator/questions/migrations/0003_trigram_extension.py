# Generated by asawicki

from django.conf import settings
from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):
    dependencies = [
        ('questions', '0001_initial'),
        ('questions', '0002_alter_subject_unique_together'),
    ]

    operations = [
        TrigramExtension(),
    ]
