# Generated by Django 2.2 on 2020-08-26 17:49

from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200825_0040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=imagekit.models.fields.ProcessedImageField(blank=True, default='User.png', null=True, upload_to='photos/%Y/'),
        ),
    ]
