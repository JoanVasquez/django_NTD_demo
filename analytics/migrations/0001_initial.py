# analytics/migrations/0001_initial.py
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PlanetEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_type", models.CharField(max_length=50)),
                ("data", models.JSONField()),
                ("consumed_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
