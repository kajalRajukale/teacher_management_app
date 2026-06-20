from django import forms

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
        ]


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "city", "address", "phone", "email"]


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
            "weekday",
            "start_time",
            "end_time",
            "room",
            "location",
            "start_date",
            "end_date",
            "notes",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
