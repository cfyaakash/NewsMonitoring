# Generated by Django 4.1.2 on 2022-11-11 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newsStories", "0006_alter_story_pub_date_alter_story_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="story",
            name="pub_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
