from django.db import models


class School(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=160, blank=True)
    level = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=80, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name


class Attendance(models.Model):
    WEEKDAY_CHOICES = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    weekday = models.CharField(max_length=3, choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["weekday", "start_time", "teacher__last_name"]

    def __str__(self):
        return f"{self.teacher} - {self.course} at {self.school}"
