from management.models import Attendance, Course, School, Teacher


def run():
    school, _ = School.objects.get_or_create(
        name="Central School",
        defaults={
            "city": "Hamburg",
            "address": "Main Street 1",
            "phone": "+49 40 123456",
            "email": "office@central-school.example",
        },
    )

    course, _ = Course.objects.get_or_create(
        name="Python Basics",
        defaults={
            "subject": "Computer Science",
            "level": "Beginner",
            "description": "Introductory programming course with Python.",
        },
    )

    teacher, _ = Teacher.objects.get_or_create(
        first_name="Anna",
        last_name="Meyer",
        defaults={
            "email": "anna.meyer@example.com",
            "phone": "+49 123 456",
            "qualification": "Python Trainer",
            "notes": "Demo teacher for local testing.",
            "active": True,
        },
    )

    Attendance.objects.get_or_create(
        teacher=teacher,
        school=school,
        course=course,
        weekday="MON",
        start_time="09:00",
        end_time="11:00",
        room="A101",
        defaults={
            "notes": "Demo attendance entry.",
        },
    )

    print("Demo data created.")


run()
