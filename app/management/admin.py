from django.contrib import admin
from .models import Attendance, Course, School, Teacher, SchoolSettings


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ("school_latitude", "school_longitude", "allowed_radius")


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
        "attendance_status",
        "standard_class",
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
        "attendance_status",
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
    actions = ["export_to_csv"]

    @admin.action(description="Export selected attendance records to CSV")
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="attendance_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            "Teacher", "School", "Date", "Time", "Status", 
            "Latitude", "Longitude", "Distance (m)", "Location", "Notes"
        ])
        
        for att in queryset.select_related("teacher", "school"):
            writer.writerow([
                att.teacher.full_name,
                att.school.name,
                att.attendance_date,
                att.attendance_time.strftime("%H:%M:%S") if att.attendance_time else "",
                att.get_attendance_status_display(),
                att.latitude or "",
                att.longitude or "",
                att.distance_from_school or "",
                att.location or "",
                att.notes,
            ])
        return response