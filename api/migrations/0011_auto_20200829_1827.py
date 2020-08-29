# Generated by Django 2.2 on 2020-08-29 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_guiderequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guiderequest',
            name='guide',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Guide', verbose_name='guide requested'),
        ),
        migrations.AlterField(
            model_name='guiderequest',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Team', verbose_name='team to be assigned'),
        ),
    ]