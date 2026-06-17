# Generated manually for starter project

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("subject", models.CharField(blank=True, max_length=160)),
                ("level", models.CharField(blank=True, max_length=120)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="School",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("city", models.CharField(blank=True, max_length=120)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("email", models.EmailField(blank=True, max_length=254)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=120)),
                ("last_name", models.CharField(max_length=120)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=80)),
                ("qualification", models.CharField(blank=True, max_length=200)),
                ("notes", models.TextField(blank=True)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.CharField(choices=[("MON", "Monday"), ("TUE", "Tuesday"), ("WED", "Wednesday"), ("THU", "Thursday"), ("FRI", "Friday"), ("SAT", "Saturday"), ("SUN", "Sunday")], max_length=3)),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("room", models.CharField(blank=True, max_length=80)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendances", to="management.course")),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendances", to="management.school")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attendances", to="management.teacher")),
            ],
            options={
                "ordering": ["weekday", "start_time", "teacher__last_name"],
            },
        ),
    ]
