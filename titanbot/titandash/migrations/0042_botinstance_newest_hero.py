# Generated by Django 2.2.8 on 2020-01-18 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0041_botinstance_next_headgear_swap'),
    ]

    operations = [
        migrations.AddField(
            model_name='botinstance',
            name='newest_hero',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Newest Hero'),
        ),
    ]
