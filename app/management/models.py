from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


class SchoolSettings(models.Model):
    school_latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        help_text="Latitude of the school (-90.0 to 90.0)"
    )
    school_longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        help_text="Longitude of the school (-180.0 to 180.0)"
    )
    allowed_radius = models.IntegerField(
        default=500,
        validators=[MinValueValidator(1)],
        help_text="Allowed attendance radius in meters"
    )

    class Meta:
        verbose_name = "School Settings"
        verbose_name_plural = "School Settings"

    def __str__(self):
        return f"School Settings (Lat: {self.school_latitude}, Lon: {self.school_longitude}, Radius: {self.allowed_radius}m)"


class School(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    school_latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    school_longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    allowed_radius_meters = models.IntegerField(
        default=500,
        validators=[MinValueValidator(1)],
        help_text="Allowed radius in meters"
    )
    
    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='teacher_profile')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=80, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers')

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Attendance(models.Model):
    class StatusChoices(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LEAVE = 'leave', 'Leave'
        CL = 'cl', 'CL (Casual Leave)'
        HALF_LEAVE = 'half_leave', 'Half Leave'
        OTHER = 'other', 'Other'

    WEEKDAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    VERIFICATION_CHOICES = [
        ('GPS_SELFIE', 'GPS + Selfie'),
        ('GPS', 'GPS Only'),
        ('SELFIE', 'Selfie Only'),
        ('MANUAL', 'Manual'),
    ]

    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('none', 'None'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances')

    attendance_date = models.DateField(default=timezone.now)
    attendance_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PRESENT)
    standard_class = models.CharField(max_length=100, blank=True, null=True, help_text="Standard/Class (STD)")

    weekday = models.CharField(max_length=20, blank=True, choices=WEEKDAY_CHOICES)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    room = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    marked_at = models.DateTimeField(default=timezone.now)
    
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Human readable location or address description")
    distance_from_school = models.FloatField(null=True, blank=True, help_text="Distance in meters")
    attendance_time = models.TimeField(default=timezone.now)
    
    device_id = models.CharField(blank=True, max_length=255, null=True)
    face_confidence = models.FloatField(blank=True, null=True)
    qr_code_data = models.CharField(blank=True, max_length=255, null=True)
    selfie_image = models.ImageField(blank=True, null=True, upload_to='attendance_selfies/')
    verification_method = models.CharField(max_length=50, choices=VERIFICATION_CHOICES, default='GPS_SELFIE')
    wifi_bssid = models.CharField(blank=True, max_length=255, null=True)
    wifi_ssid = models.CharField(blank=True, max_length=255, null=True)

    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='none')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendances')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-attendance_date', 'weekday', 'start_time', 'teacher__last_name']
        constraints = [
            models.UniqueConstraint(fields=['teacher', 'attendance_date'], name='unique_teacher_attendance_per_day')
        ]

    def save(self, *args, **kwargs):
        if not self.weekday and self.attendance_date:
            weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            self.weekday = weekdays[self.attendance_date.weekday()]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} - {self.attendance_date}"