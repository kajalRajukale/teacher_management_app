from django.contrib import admin

from .models import Attendance, Course, School, Teacher


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "email", "phone")
    search_fields = ("name", "city", "address", "email")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "level")
    search_fields = ("name", "subject", "level")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email", "phone", "active")
    list_filter = ("active",)
    search_fields = ("first_name", "last_name", "email", "qualification")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "school",
        "course",
        "weekday",
        "start_time",
        "end_time",
        "room",
    )
    list_filter = ("weekday", "school", "course")
    search_fields = (
        "teacher__first_name",
        "teacher__last_name",
        "school__name",
        "course__name",
        "room",
    )
