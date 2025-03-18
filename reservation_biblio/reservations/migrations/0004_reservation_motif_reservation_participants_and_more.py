# Generated by Django 5.1.4 on 2025-01-09 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservations", "0003_remove_reservation_box_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="motif",
            field=models.TextField(default="Motif par défaut"),
        ),
        migrations.AddField(
            model_name="reservation",
            name="participants",
            field=models.CharField(default="Aucune", max_length=255),
        ),
        migrations.AddField(
            model_name="reservation",
            name="student",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="reservations.student",
            ),
        ),
        migrations.AlterField(
            model_name="reservation",
            name="room",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="reservations.room",
            ),
        ),
    ]
