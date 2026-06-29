from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Interviewer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="InterviewTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("duration_minutes", models.PositiveIntegerField()),
                (
                    "interviewers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="interview_templates",
                        to="interviews.interviewer",
                    ),
                ),
            ],
        ),
    ]
