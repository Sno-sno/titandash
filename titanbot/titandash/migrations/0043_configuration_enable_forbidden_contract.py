# Generated by Django 2.2.10 on 2020-03-12 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0042_botinstance_newest_hero'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='enable_forbidden_contract',
            field=models.BooleanField(default=False, help_text='Enable forbidden contract tapping skill minigame..', verbose_name='Enable Forbidden Contract'),
        ),
    ]