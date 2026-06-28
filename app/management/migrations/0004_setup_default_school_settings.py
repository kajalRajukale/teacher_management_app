from django.db import migrations

def create_default_school_settings(apps, schema_editor):
    SchoolSettings = apps.get_model('management', 'SchoolSettings')
    # Create the default school settings if none exist
    if not SchoolSettings.objects.exists():
        SchoolSettings.objects.create(
            school_latitude=18.4276826,
            school_longitude=73.8783014,
            allowed_radius=100
        )
        
    # Also set default coordinates for the first School record to align them
    School = apps.get_model('management', 'School')
    school = School.objects.first()
    if school:
        school.school_latitude = 18.4276826
        school.school_longitude = 73.8783014
        school.allowed_radius_meters = 100
        school.save()

class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_attendance_standard_class'),
    ]

    operations = [
        migrations.RunPython(create_default_school_settings),
    ]
