from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class School(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Geo-fencing fields
    school_latitude = models.FloatField(null=True, blank=True)
    school_longitude = models.FloatField(null=True, blank=True)
    allowed_radius_meters = models.IntegerField(default=100, help_text="Allowed radius in meters")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Course(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    level = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='teacher_profile')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers')
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=80, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["last_name", "first_name"]


class Attendance(models.Model):
    class StatusChoices(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LEAVE = 'LEAVE', 'Leave'
        CL = 'CL', 'CL (Casual Leave)'
        HALF_DAY = 'HALF_DAY', 'Half Day'

    WEEKDAY_CHOICES = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="attendances")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="attendances")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendances")

    # Timestamps & date
    attendance_date = models.DateField(default=timezone.now)
    attendance_time = models.TimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    marked_at = models.DateTimeField(default=timezone.now)  # For backwards compatibility

    # Dropdown status
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PRESENT
    )

    # Location fields
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Human readable location or address description")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    distance_from_school = models.FloatField(null=True, blank=True, help_text="Distance from school in meters")

    weekday = models.CharField(max_length=20, choices=WEEKDAY_CHOICES, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    room = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    # Future Ready fields
    verification_method = models.CharField(
        max_length=50,
        default='GPS',
        choices=[
            ('GPS', 'GPS'),
            ('SELFIE', 'Selfie Verification'),
            ('FACE', 'Face Recognition'),
            ('QR', 'QR Code'),
            ('DEVICE', 'Device Verification'),
            ('WIFI', 'WiFi Verification')
        ]
    )
    selfie_image = models.ImageField(upload_to='attendance_selfies/', null=True, blank=True)
    face_confidence = models.FloatField(null=True, blank=True)
    qr_code_data = models.CharField(max_length=255, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    wifi_ssid = models.CharField(max_length=255, null=True, blank=True)
    wifi_bssid = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Automatically populate date and time if not set
        if not self.attendance_date:
            self.attendance_date = timezone.now().date()
        if not self.attendance_time:
            self.attendance_time = timezone.now().time()
        
        # Set weekday automatically
        if self.attendance_date:
            self.weekday = self.attendance_date.strftime("%a").upper()[:3]
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} - {self.attendance_date}"

    class Meta:
        ordering = ["-attendance_date", "weekday", "start_time", "teacher__last_name"]
        constraints = [
            models.UniqueConstraint(fields=["teacher", "attendance_date"], name="unique_teacher_attendance_per_day")
        ]