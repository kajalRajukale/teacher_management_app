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
            "attendance_status", 
            "standard_class",
            "weekday", 
            "start_time", 
            "end_time", 
            "room", 
            "notes", 
            "latitude", 
            "longitude", 
            "location", 
            "distance_from_school",
            "verification_method",
            "selfie_image",
            "approval_status",
        ]
        widgets = {
            "attendance_status": forms.Select(attrs={"class": "form-select"}),
            "attendance_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "attendance_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "standard_class": forms.TextInput(attrs={"placeholder": "e.g. 10th Grade", "class": "form-control"}),
            "verification_method": forms.Select(attrs={"class": "form-select"}),
            "approval_status": forms.Select(attrs={"class": "form-select"}),
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
    Mobile-friendly attendance mark form with GPS + Selfie verification.
    """
    class Meta:
        model = Attendance
        fields = ["teacher", "standard_class", "attendance_status"]
        widgets = {
            "standard_class": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 10th Grade, Class A",
            }),
            "teacher": forms.Select(attrs={
                "class": "form-select",
            }),
            "attendance_status": forms.Select(attrs={
                "class": "form-select",
            }),
        }
