# Generated by Django 3.2.16 on 2023-09-13 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_remove_post_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='text',
            field=models.TextField(default=0, verbose_name='Текст'),
            preserve_default=False,
        ),
    ]
