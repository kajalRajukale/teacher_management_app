import csv
import io
import json
import math
import logging
from collections import Counter
from datetime import date, timedelta

from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .forms import AttendanceForm, CourseForm, SchoolForm, TeacherForm, TeacherAttendanceForm
from .models import Attendance, Course, School, Teacher, SchoolSettings
from .utils import haversine

logger = logging.getLogger(__name__)


def dashboard(request):
    """
    Dashboard showing resources overview and statistics for TODAY.
    """
    today = timezone.now().date()
    
    # Dashboard Statistics for Today
    today_attendances = Attendance.objects.filter(attendance_date=today)
    
    total_teachers = Teacher.objects.filter(active=True).count()
    present_count = today_attendances.filter(attendance_status="PRESENT").count()
    absent_count = today_attendances.filter(attendance_status="ABSENT").count()
    leave_count = today_attendances.filter(attendance_status="LEAVE").count()
    cl_count = today_attendances.filter(attendance_status="CL").count()
    half_day_count = today_attendances.filter(attendance_status="HALF_DAY").count()

    return render(
        request,
        "management/dashboard.html",
        {
            "teacher_count": total_teachers,
            "school_count": School.objects.count(),
            "course_count": Course.objects.count(),
            "attendance_count": Attendance.objects.count(),
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "cl_count": cl_count,
            "half_day_count": half_day_count,
            "today": today,
            "upcoming_attendances": Attendance.objects.select_related(
                "teacher", "school"
            ).order_by("-attendance_date", "-attendance_time")[:10],
        },
    )


@login_required
def attendance_mark(request):
    """
    Simple, mobile-friendly interface for teachers to mark their attendance.
    Also supports admins who can select any teacher/school.
    """
    today = timezone.now().date()
    
    # Check if the logged-in user has a Teacher profile
    try:
        current_teacher = request.user.teacher_profile
        is_teacher = True
    except (AttributeError, Teacher.DoesNotExist):
        current_teacher = None
        is_teacher = False

    # Security: teachers can only mark their own attendance
    if is_teacher:
        teachers = Teacher.objects.filter(pk=current_teacher.pk)
        schools = School.objects.filter(pk=current_teacher.school.pk) if current_teacher.school else School.objects.all()
    else:
        teachers = Teacher.objects.filter(active=True)
        schools = School.objects.all()

    # Pre-resolve school location and radius for the teacher (for frontend validation)
    global_settings = SchoolSettings.objects.first()
    
    if is_teacher and current_teacher.school:
        s_lat = current_teacher.school.school_latitude
        s_lng = current_teacher.school.school_longitude
        s_radius = current_teacher.school.allowed_radius_meters
    else:
        s_lat, s_lng, s_radius = None, None, None
        
    # Global settings overrides if configured
    if global_settings and global_settings.school_latitude is not None and global_settings.school_longitude is not None:
        s_lat = global_settings.school_latitude
        s_lng = global_settings.school_longitude
        s_radius = global_settings.allowed_radius

    if request.method == "POST":
        status = "PRESENT"  # Always mark as PRESENT from the simplified mark page
        standard_class = request.POST.get("standard_class", "")
        notes = request.POST.get("notes", "")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Determine teacher & school
        if is_teacher:
            teacher = current_teacher
            school = current_teacher.school
        else:
            teacher_id = request.POST.get("teacher_id")
            school_id = request.POST.get("school_id")
            teacher = get_object_or_404(Teacher, pk=teacher_id) if teacher_id else None
            school = get_object_or_404(School, pk=school_id) if school_id else None

        if not teacher:
            return render(request, "management/attendance_mark.html", {
                "error": "Teacher profile not found.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
                "school_latitude": s_lat,
                "school_longitude": s_lng,
                "allowed_radius": s_radius,
            })

        lat_val = float(latitude) if latitude else None
        lng_val = float(longitude) if longitude else None

        # Determine school coordinates and radius
        school_lat, school_lng, allowed_radius = None, None, None
        
        # 1. First check global settings
        if global_settings and global_settings.school_latitude is not None and global_settings.school_longitude is not None:
            school_lat = global_settings.school_latitude
            school_lng = global_settings.school_longitude
            allowed_radius = global_settings.allowed_radius
        # 2. Then check specific school
        elif school:
            school_lat = school.school_latitude
            school_lng = school.school_longitude
            allowed_radius = school.allowed_radius_meters

        # If school is not pre-assigned and not in global settings, attempt to resolve closest school using GPS
        if not school_lat or not school_lng:
            if lat_val and lng_val:
                closest_school = None
                min_dist = float('inf')
                for s in School.objects.all():
                    if s.school_latitude and s.school_longitude:
                        dist = haversine(lat_val, lng_val, s.school_latitude, s.school_longitude)
                        if dist < min_dist:
                            min_dist = dist
                            closest_school = s
                if closest_school:
                    school = closest_school
                    school_lat = closest_school.school_latitude
                    school_lng = closest_school.school_longitude
                    allowed_radius = closest_school.allowed_radius_meters
            
            if not school_lat or not school_lng:
                logger.warning(f"Failed attendance attempt: School location not configured. Teacher {teacher.full_name}")
                return render(request, "management/attendance_mark.html", {
                    "error": "School location has not been configured. Please contact the administrator.",
                    "teachers": teachers,
                    "schools": schools,
                    "is_teacher": is_teacher,
                    "today": today,
                    "school_latitude": s_lat,
                    "school_longitude": s_lng,
                    "allowed_radius": s_radius,
                })

        # Check if already marked today
        existing = Attendance.objects.filter(
            teacher=teacher, attendance_date=today
        ).exists()
        if existing:
            return render(request, "management/attendance_mark.html", {
                "error": f"Attendance already marked for today.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
                "school_latitude": s_lat,
                "school_longitude": s_lng,
                "allowed_radius": s_radius,
            })

        # For PRESENT, we strictly enforce the GPS check
        distance = None
        if lat_val is None or lng_val is None:
            return render(request, "management/attendance_mark.html", {
                "error": "GPS coordinates are required to submit attendance.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
                "school_latitude": s_lat,
                "school_longitude": s_lng,
                "allowed_radius": s_radius,
            })
        
        # Validate coordinates are within valid range
        if not (-90 <= lat_val <= 90) or not (-180 <= lng_val <= 180):
            return render(request, "management/attendance_mark.html", {
                "error": "Invalid GPS coordinates structure.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
                "school_latitude": s_lat,
                "school_longitude": s_lng,
                "allowed_radius": s_radius,
            })

        distance = haversine(lat_val, lng_val, school_lat, school_lng)
        
        # Debug logs
        print(f"Teacher Location: {lat_val}, {lng_val}")
        print(f"School Location: {school_lat}, {school_lng}")
        print(f"Calculated Distance: {distance} meters")

        if distance is None or distance > allowed_radius:
            # Log failed attempt
            logger.warning(
                f"Failed attendance attempt: Teacher {teacher.full_name} (ID: {teacher.id}) "
                f"tried to mark '{status}' from outside school premises. "
                f"Teacher Location: ({lat_val}, {lng_val}), School Location: ({school_lat}, {school_lng}), "
                f"Distance: {distance if distance is not None else 'N/A'}m, Allowed Radius: {allowed_radius}m"
            )
            return render(request, "management/attendance_mark.html", {
                "error": "You are outside the school campus. Attendance can only be marked when you are near the school.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
                "distance": int(distance) if distance is not None else None,
                "max_distance": allowed_radius,
                "school_latitude": s_lat,
                "school_longitude": s_lng,
                "allowed_radius": s_radius,
            })

        # Save location info
        location_desc = f"GPS: {lat_val:.6f}, {lng_val:.6f}"

        # Default school fallback if none resolved
        if not school:
            school = School.objects.first()

        attendance = Attendance.objects.create(
            teacher=teacher,
            school=school,
            attendance_date=today,
            attendance_time=timezone.now().time(),
            attendance_status=status,
            standard_class=standard_class,
            notes=notes,
            latitude=lat_val,
            longitude=lng_val,
            location=location_desc,
            distance_from_school=distance,
            created_at=timezone.now(),
        )

        return render(request, "management/attendance_mark.html", {
            "success": f"Attendance marked: '{attendance.get_attendance_status_display()}' at {school.name}.",
            "teachers": teachers,
            "schools": schools,
            "is_teacher": is_teacher,
            "today": today,
            "school_latitude": s_lat,
            "school_longitude": s_lng,
            "allowed_radius": s_radius,
        })

    return render(request, "management/attendance_mark.html", {
        "teachers": teachers,
        "schools": schools,
        "is_teacher": is_teacher,
        "today": today,
        "school_latitude": s_lat,
        "school_longitude": s_lng,
        "allowed_radius": s_radius,
    })


def attendance_list(request):
    """
    Search and filter attendances with rich location parameters.
    """
    query = request.GET.get("q", "")
    school_id = request.GET.get("school", "")
    status = request.GET.get("status", "")
    date_filter = request.GET.get("date", "")

    attendances = Attendance.objects.select_related("teacher", "school").order_by("-attendance_date", "-attendance_time")

    if query:
        attendances = attendances.filter(
            Q(teacher__first_name__icontains=query) |
            Q(teacher__last_name__icontains=query) |
            Q(school__name__icontains=query)
        )
    if school_id:
        attendances = attendances.filter(school_id=school_id)
    if status:
        attendances = attendances.filter(attendance_status=status)
    if date_filter:
        attendances = attendances.filter(attendance_date=date_filter)

    schools = School.objects.all()
    statuses = Attendance.StatusChoices.choices

    return render(
        request,
        "management/attendance_list.html",
        {
            "attendances": attendances,
            "schools": schools,
            "statuses": statuses,
            "query": query,
            "selected_school": int(school_id) if school_id else None,
            "selected_status": status,
            "selected_date": date_filter,
        },
    )


def attendance_history(request):
    teacher_id = request.GET.get("teacher")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    month = request.GET.get("month")

    attendances = Attendance.objects.select_related("teacher", "school")

    if teacher_id:
        attendances = attendances.filter(teacher_id=teacher_id)
    if date_from:
        attendances = attendances.filter(attendance_date__gte=date_from)
    if date_to:
        attendances = attendances.filter(attendance_date__lte=date_to)
    if month:
        attendances = attendances.filter(attendance_date__month=month)

    daily_view = {}
    for att in attendances:
        day = att.attendance_date.isoformat()
        if day not in daily_view:
            daily_view[day] = []
        daily_view[day].append(att)

    monthly_summary = (
        attendances
        .values("attendance_date__year", "attendance_date__month")
        .annotate(
            total=Count("id"),
            present=Count("id", filter=Q(attendance_status="PRESENT")),
            absent=Count("id", filter=Q(attendance_status="ABSENT")),
            leave=Count("id", filter=Q(attendance_status="LEAVE")),
            cl=Count("id", filter=Q(attendance_status="CL")),
            half_day=Count("id", filter=Q(attendance_status="HALF_DAY")),
        )
        .order_by("-attendance_date__year", "-attendance_date__month")
    )

    return render(request, "management/attendance_history.html", {
        "attendances": attendances,
        "daily_view": dict(sorted(daily_view.items(), reverse=True)),
        "monthly_summary": monthly_summary,
        "teachers": Teacher.objects.all(),
        "selected_teacher": teacher_id,
        "selected_date_from": date_from,
        "selected_date_to": date_to,
        "selected_month": month,
        "total_count": attendances.count(),
        "present_count": attendances.filter(attendance_status="PRESENT").count(),
        "absent_count": attendances.filter(attendance_status="ABSENT").count(),
        "leave_count": attendances.filter(attendance_status="LEAVE").count(),
        "cl_count": attendances.filter(attendance_status="CL").count(),
        "half_day_count": attendances.filter(attendance_status="HALF_DAY").count(),
    })


def attendance_export(request):
    teacher_id = request.GET.get("teacher")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    fmt = request.GET.get("format", "csv")

    attendances = Attendance.objects.select_related("teacher", "school")

    if teacher_id:
        attendances = attendances.filter(teacher_id=teacher_id)
    if date_from:
        attendances = attendances.filter(attendance_date__gte=date_from)
    if date_to:
        attendances = attendances.filter(attendance_date__lte=date_to)

    if fmt == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="attendance_report_{timezone.now().strftime("%Y%m%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Teacher", "School", "Date", "Time", "Status", "Standard/Class", "Created At",
            "Location", "Latitude", "Longitude", "Distance (m)", "Notes",
        ])
        for att in attendances:
            writer.writerow([
                att.teacher.full_name,
                att.school.name,
                att.attendance_date,
                att.attendance_time.strftime("%H:%M:%S") if att.attendance_time else "",
                att.get_attendance_status_display(),
                att.standard_class or "",
                att.created_at.strftime("%Y-%m-%d %H:%M:%S") if att.created_at else "",
                att.location or "",
                att.latitude or "",
                att.longitude or "",
                att.distance_from_school or "",
                att.notes,
            ])
        return response

    return render(request, "management/attendance_export.html", {
        "teachers": Teacher.objects.all(),
    })


def attendance_report(request):
    teacher_id = request.GET.get("teacher")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    attendances = Attendance.objects.select_related("teacher", "school", "course")

    if teacher_id:
        attendances = attendances.filter(teacher_id=teacher_id)
    if date_from:
        attendances = attendances.filter(attendance_date__gte=date_from)
    if date_to:
        attendances = attendances.filter(attendance_date__lte=date_to)

    status_summary = attendances.values("attendance_status").annotate(count=Count("id"))
    teacher_summary = (
        attendances.values("teacher__first_name", "teacher__last_name")
        .annotate(
            total=Count("id"),
            present=Count("id", filter=Q(attendance_status="PRESENT")),
            absent=Count("id", filter=Q(attendance_status="ABSENT")),
            leave=Count("id", filter=Q(attendance_status="LEAVE")),
            cl=Count("id", filter=Q(attendance_status="CL")),
            half_day=Count("id", filter=Q(attendance_status="HALF_DAY")),
        )
        .order_by("teacher__last_name")
    )

    status_map = dict(Attendance.StatusChoices.choices)
    status_summary_list = [
        {"status": s["attendance_status"], "label": status_map.get(s["attendance_status"], s["attendance_status"]), "count": s["count"]}
        for s in status_summary
    ]

    return render(
        request,
        "management/attendance_report.html",
        {
            "attendances": attendances,
            "status_summary": status_summary_list,
            "teacher_summary": teacher_summary,
            "teachers": Teacher.objects.all(),
            "selected_teacher": teacher_id,
            "selected_date_from": date_from,
            "selected_date_to": date_to,
            "total_count": attendances.count(),
            "present_count": attendances.filter(attendance_status="PRESENT").count(),
            "absent_count": attendances.filter(attendance_status="ABSENT").count(),
            "leave_count": attendances.filter(attendance_status="LEAVE").count(),
            "cl_count": attendances.filter(attendance_status="CL").count(),
            "half_day_count": attendances.filter(attendance_status="HALF_DAY").count(),
        },
    )


def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, "management/teacher_list.html", {"teachers": teachers})


def teacher_create(request):
    form = TeacherForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("teacher_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Create teacher", "back_url": "teacher_list"},
    )


def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("teacher_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Edit teacher", "back_url": "teacher_list"},
    )


def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.delete()
        return redirect("teacher_list")
    return render(
        request,
        "management/confirm_delete.html",
        {"object": teacher, "title": "Delete teacher", "back_url": "teacher_list"},
    )


def school_list(request):
    schools = School.objects.all()
    return render(request, "management/school_list.html", {"schools": schools})


def school_create(request):
    form = SchoolForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("school_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Create school", "back_url": "school_list"},
    )


def school_update(request, pk):
    school = get_object_or_404(School, pk=pk)
    form = SchoolForm(request.POST or None, instance=school)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("school_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Edit school", "back_url": "school_list"},
    )


def school_delete(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == "POST":
        school.delete()
        return redirect("school_list")
    return render(
        request,
        "management/confirm_delete.html",
        {"object": school, "title": "Delete school", "back_url": "school_list"},
    )


def course_list(request):
    courses = Course.objects.all()
    return render(request, "management/course_list.html", {"courses": courses})


def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("course_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Create course", "back_url": "course_list"},
    )


def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("course_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Edit course", "back_url": "course_list"},
    )


def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect("course_list")
    return render(
        request,
        "management/confirm_delete.html",
        {"object": course, "title": "Delete course", "back_url": "course_list"},
    )


def attendance_create(request):
    form = AttendanceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("attendance_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Create attendance", "back_url": "attendance_list"},
    )


def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    form = AttendanceForm(request.POST or None, instance=attendance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("attendance_list")
    return render(
        request,
        "management/form.html",
        {"form": form, "title": "Edit attendance", "back_url": "attendance_list"},
    )


def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == "POST":
        attendance.delete()
        return redirect("attendance_list")
    return render(
        request,
        "management/confirm_delete.html",
        {
            "object": attendance,
            "title": "Delete attendance",
            "back_url": "attendance_list",
        },
    )


# ---------- API Views ----------

def teacher_to_dict(teacher):
    return {
        "id": teacher.id,
        "first_name": teacher.first_name,
        "last_name": teacher.last_name,
        "full_name": teacher.full_name,
        "email": teacher.email,
        "phone": teacher.phone,
        "qualification": teacher.qualification,
        "notes": teacher.notes,
        "active": teacher.active,
    }


def school_to_dict(school):
    return {
        "id": school.id,
        "name": school.name,
        "city": school.city,
        "address": school.address,
        "phone": school.phone,
        "email": school.email,
        "latitude": float(school.school_latitude) if school.school_latitude else None,
        "longitude": float(school.school_longitude) if school.school_longitude else None,
        "school_latitude": float(school.school_latitude) if school.school_latitude else None,
        "school_longitude": float(school.school_longitude) if school.school_longitude else None,
        "geo_fence_radius": school.allowed_radius_meters,
        "allowed_radius_meters": school.allowed_radius_meters,
    }


def course_to_dict(course):
    return {
        "id": course.id,
        "name": course.name,
        "subject": course.subject,
        "level": course.level,
        "description": course.description,
    }


def attendance_to_dict(attendance):
    return {
        "id": attendance.id,
        "teacher": teacher_to_dict(attendance.teacher),
        "school": school_to_dict(attendance.school),
        "course": course_to_dict(attendance.course) if attendance.course else None,
        "attendance_date": attendance.attendance_date.isoformat(),
        "attendance_time": attendance.attendance_time.isoformat() if attendance.attendance_time else None,
        "status": attendance.attendance_status,
        "status_display": attendance.get_attendance_status_display(),
        "standard_class": attendance.standard_class,
        "location": attendance.location,
        "latitude": float(attendance.latitude) if attendance.latitude else None,
        "longitude": float(attendance.longitude) if attendance.longitude else None,
        "distance_from_school": attendance.distance_from_school,
        "marked_at": attendance.marked_at.isoformat() if attendance.marked_at else None,
        "created_at": attendance.created_at.isoformat() if attendance.created_at else None,
        "notes": attendance.notes,
        "verification_method": attendance.verification_method,
    }


def read_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON"}, status=400)


def api_teacher_list(request):
    teachers = Teacher.objects.all()
    return JsonResponse([teacher_to_dict(teacher) for teacher in teachers], safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_teacher_create(request):
    payload, error = read_json(request)
    if error:
        return error

    required = ["first_name", "last_name"]
    missing = [field for field in required if not payload.get(field)]

    if missing:
        return JsonResponse({"error": "Missing fields", "fields": missing}, status=400)

    teacher = Teacher.objects.create(
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        email=payload.get("email", ""),
        phone=payload.get("phone", ""),
        qualification=payload.get("qualification", ""),
        notes=payload.get("notes", ""),
        active=payload.get("active", True),
    )
    return JsonResponse(teacher_to_dict(teacher), status=201)


def api_teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return JsonResponse(teacher_to_dict(teacher))


@csrf_exempt
@require_http_methods(["POST", "PUT", "PATCH"])
def api_teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    payload, error = read_json(request)
    if error:
        return error

    for field in [
        "first_name",
        "last_name",
        "email",
        "phone",
        "qualification",
        "notes",
        "active",
    ]:
        if field in payload:
            setattr(teacher, field, payload[field])

    teacher.save()
    return JsonResponse(teacher_to_dict(teacher))


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.delete()
    return JsonResponse({"deleted": True})


def api_school_list(request):
    return JsonResponse(
        [school_to_dict(school) for school in School.objects.all()],
        safe=False,
    )


def api_course_list(request):
    return JsonResponse(
        [course_to_dict(course) for course in Course.objects.all()],
        safe=False,
    )


def api_attendance_list(request):
    attendances = Attendance.objects.select_related("teacher", "school", "course")
    return JsonResponse(
        [attendance_to_dict(attendance) for attendance in attendances],
        safe=False,
    )


@csrf_exempt
@require_http_methods(["POST"])
def api_attendance_create(request):
    payload, error = read_json(request)
    if error:
        return error

    required = ["teacher_id", "school_id"]
    missing = [field for field in required if not payload.get(field)]

    if missing:
        return JsonResponse({"error": "Missing fields", "fields": missing}, status=400)

    teacher = get_object_or_404(Teacher, pk=payload["teacher_id"])
    school = get_object_or_404(School, pk=payload["school_id"])

    status = payload.get("status") or payload.get("attendance_status") or "PRESENT"
    standard_class = payload.get("standard_class", "")
    valid_statuses = [s[0] for s in Attendance.StatusChoices.choices]
    if status not in valid_statuses:
        return JsonResponse(
            {"error": "Invalid status", "valid": valid_statuses},
            status=400,
        )

    today = timezone.now().date()
    existing = Attendance.objects.filter(
        teacher=teacher,
        attendance_date=today,
    )
    if existing.exists():
        return JsonResponse(
            {"error": f"Attendance already recorded for {teacher.full_name} on {today}"},
            status=409,
        )

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    # Determine school coordinates and radius
    global_settings = SchoolSettings.objects.first()
    
    school_lat, school_lng, allowed_radius = None, None, None
    if global_settings and global_settings.school_latitude is not None and global_settings.school_longitude is not None:
        school_lat = global_settings.school_latitude
        school_lng = global_settings.school_longitude
        allowed_radius = global_settings.allowed_radius
    else:
        school_lat = school.school_latitude
        school_lng = school.school_longitude
        allowed_radius = school.allowed_radius_meters

    if not school_lat or not school_lng:
        logger.warning(f"Failed API attendance attempt: School location not configured. Teacher {teacher.full_name}")
        return JsonResponse({"error": "School location has not been configured. Please contact the administrator."}, status=400)

    distance = None
    if status in ["PRESENT", "HALF_DAY"]:
        if latitude is None or longitude is None:
            return JsonResponse({"error": "GPS coordinates are required to mark attendance."}, status=400)

        try:
            teacher_lat = float(latitude)
            teacher_lon = float(longitude)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid GPS coordinates structure."}, status=400)

        if not (-90 <= teacher_lat <= 90) or not (-180 <= teacher_lon <= 180):
            return JsonResponse({"error": "Invalid GPS coordinates structure."}, status=400)

        distance = haversine(teacher_lat, teacher_lon, school_lat, school_lng)

        # Print detailed debug logs
        print(f"Teacher Location: {teacher_lat}, {teacher_lon}")
        print(f"School Location: {school_lat}, {school_lng}")
        print(f"Calculated Distance: {distance} meters")

        if distance is None or distance > allowed_radius:
            logger.warning(
                f"Failed API attendance attempt: Teacher {teacher.full_name} (ID: {teacher.id}) "
                f"tried to mark '{status}' from outside school premises. "
                f"Teacher Location: ({teacher_lat}, {teacher_lon}), School Location: ({school_lat}, {school_lng}), "
                f"Distance: {distance if distance is not None else 'N/A'}m, Allowed Radius: {allowed_radius}m"
            )
            return JsonResponse(
                {"error": "You are outside the school campus. Attendance can only be marked when you are near the school."},
                status=403,
            )
    else:
        # ABSENT, LEAVE, CL
        if latitude is not None and longitude is not None:
            try:
                teacher_lat = float(latitude)
                teacher_lon = float(longitude)
                if (-90 <= teacher_lat <= 90) and (-180 <= teacher_lon <= 180):
                    distance = haversine(teacher_lat, teacher_lon, school_lat, school_lng)
            except (ValueError, TypeError):
                pass

    location_desc = None
    if latitude is not None and longitude is not None:
        try:
            location_desc = f"GPS: {float(latitude):.6f}, {float(longitude):.6f}"
        except (ValueError, TypeError):
            pass

    attendance = Attendance.objects.create(
        teacher=teacher,
        school=school,
        attendance_date=today,
        attendance_time=timezone.now().time(),
        attendance_status=status,
        standard_class=standard_class,
        notes=payload.get("notes", ""),
        latitude=float(latitude) if latitude is not None else None,
        longitude=float(longitude) if longitude is not None else None,
        location=location_desc,
        distance_from_school=distance,
        created_at=timezone.now(),
    )

    return JsonResponse(attendance_to_dict(attendance), status=201)


@csrf_exempt
@require_http_methods(["POST"])
def api_validate_gps(request):
    payload, error = read_json(request)
    if error:
        return error

    school_id = payload.get("school_id")
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    if latitude is None or longitude is None:
        return JsonResponse({"error": "Missing latitude or longitude"}, status=400)

    global_settings = SchoolSettings.objects.first()
    
    school_lat, school_lng, allowed_radius = None, None, None
    school_name = "School Settings"
    
    if global_settings and global_settings.school_latitude is not None and global_settings.school_longitude is not None:
        school_lat = global_settings.school_latitude
        school_lng = global_settings.school_longitude
        allowed_radius = global_settings.allowed_radius
    elif school_id:
        school = get_object_or_404(School, pk=school_id)
        school_lat = school.school_latitude
        school_lng = school.school_longitude
        allowed_radius = school.allowed_radius_meters
        school_name = school.name
        
    if not school_lat or not school_lng:
        return JsonResponse({"error": "School GPS coordinates are not configured"}, status=400)

    distance = haversine(latitude, longitude, school_lat, school_lng)
    within = distance <= allowed_radius

    return JsonResponse({
        "within": within,
        "distance": int(distance),
        "max_distance": allowed_radius,
        "school": school_name,
    })
