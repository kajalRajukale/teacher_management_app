from django import forms
from django.core.exceptions import ValidationError
from .models import Attendance, Course, School, Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "qualification",
            "notes",
            "active",
            "user",
            "school",
        ]


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            "name", 
            "city", 
            "address", 
            "phone", 
            "email", 
            "school_latitude", 
            "school_longitude", 
            "allowed_radius_meters"
        ]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "subject", "level", "description"]


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = [
            "teacher", 
            "school", 
            "course", 
            "attendance_date", 
            "attendance_time", 
            "status", 
            "weekday", 
            "start_time", 
            "end_time", 
            "room", 
            "notes", 
            "latitude", 
            "longitude", 
            "location", 
            "distance_from_school"
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "status-select"}),
            "attendance_date": forms.DateInput(attrs={"type": "date"}),
            "attendance_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get("teacher")
        attendance_date = cleaned_data.get("attendance_date")

        if teacher and attendance_date:
            existing = Attendance.objects.filter(
                teacher=teacher,
                attendance_date=attendance_date,
            )
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(
                    f"{teacher.full_name} already has an attendance record for {attendance_date}. "
                    "Only one attendance entry per teacher per day is allowed."
                )

        return cleaned_data


class TeacherAttendanceForm(forms.ModelForm):
    """
    Simplified, mobile-friendly attendance mark form used by teachers.
    Contains ONLY the status field as requested.
    """
    class Meta:
        model = Attendance
        fields = ["status"]
        widgets = {
            "status": forms.Select(attrs={"class": "status-select"}),
        }