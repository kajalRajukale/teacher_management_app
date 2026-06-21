from django.contrib import admin
from .models import Attendance, Course, School, Teacher


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name", 
        "city", 
        "email", 
        "phone", 
        "school_latitude", 
        "school_longitude", 
        "allowed_radius_meters"
    )
    search_fields = ("name", "city", "address", "email")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "level")
    search_fields = ("name", "subject", "level")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email", "phone", "user", "school", "active")
    list_filter = ("active", "school")
    search_fields = ("first_name", "last_name", "email", "qualification")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "school",
        "status",
        "attendance_date",
        "attendance_time",
        "location",
        "latitude",
        "longitude",
        "distance_from_school",
        "verification_method",
        "created_at",
    )

    list_filter = (
        "status",
        "attendance_date",
        "school",
        "verification_method",
    )

    search_fields = (
        "teacher__first_name",
        "teacher__last_name",
        "school__name",
        "location",
    )

    readonly_fields = ("created_at", "marked_at")