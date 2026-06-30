from django.db import migrations
from faker import Faker


TEMPLATES = [
    {"name": "HR Screening", "duration_minutes": 30},
    {"name": "Technical Interview", "duration_minutes": 60},
    {"name": "System Design", "duration_minutes": 90},
    {"name": "Behavioural Interview", "duration_minutes": 45},
]


def seed_data(apps, schema_editor):
    Interviewer = apps.get_model("interviews", "Interviewer")
    InterviewTemplate = apps.get_model("interviews", "InterviewTemplate")

    fake = Faker()
    Faker.seed(42)

    interviewers = [Interviewer.objects.create(name=fake.name()) for _ in range(6)]

    for i, tmpl in enumerate(TEMPLATES):
        template = InterviewTemplate.objects.create(**tmpl)
        # Assign 2–3 interviewers per template, rotating through the pool.
        assigned = interviewers[i % len(interviewers) : i % len(interviewers) + 3]
        template.interviewers.set(assigned)


def unseed_data(apps, schema_editor):
    apps.get_model("interviews", "InterviewTemplate").objects.all().delete()
    apps.get_model("interviews", "Interviewer").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("interviews", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]
