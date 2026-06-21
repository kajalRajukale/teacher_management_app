import csv
import io
import json
import math
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
from .models import Attendance, Course, School, Teacher
from .utils import haversine


def dashboard(request):
    """
    Dashboard showing resources overview and statistics for TODAY.
    """
    today = timezone.now().date()
    
    # Dashboard Statistics for Today
    today_attendances = Attendance.objects.filter(attendance_date=today)
    
    total_teachers = Teacher.objects.filter(active=True).count()
    present_count = today_attendances.filter(status="PRESENT").count()
    absent_count = today_attendances.filter(status="ABSENT").count()
    leave_count = today_attendances.filter(status="LEAVE").count()
    cl_count = today_attendances.filter(status="CL").count()
    half_day_count = today_attendances.filter(status="HALF_DAY").count()

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

    if request.method == "POST":
        status = request.POST.get("status", "PRESENT")
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
            })

        lat_val = float(latitude) if latitude else None
        lng_val = float(longitude) if longitude else None

        # If school is not pre-assigned, attempt to resolve closest school using GPS
        if not school:
            if lat_val and lng_val:
                closest_school = None
                min_dist = float('inf')
                for s in School.objects.all():
                    if s.school_latitude and s.school_longitude:
                        dist = haversine(lat_val, lng_val, s.school_latitude, s.school_longitude)
                        if dist < min_dist:
                            min_dist = dist
                            closest_school = s
                school = closest_school
            
            if not school:
                return render(request, "management/attendance_mark.html", {
                    "error": "No school could be identified. Please configure your school location first.",
                    "teachers": teachers,
                    "schools": schools,
                    "is_teacher": is_teacher,
                    "today": today,
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
            })

        # Verify GPS coordinates
        teacher_lat = lat_val
        teacher_lon = lng_val
        school_lat = school.school_latitude if school else None
        school_lon = school.school_longitude if school else None

        if teacher_lat is None or teacher_lon is None:
            return render(request, "management/attendance_mark.html", {
                "error": "GPS coordinates are required to submit attendance.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
            })

        if school_lat is None or school_lon is None:
            return render(request, "management/attendance_mark.html", {
                "error": f"School '{school.name}' coordinates are not configured. Cannot verify geo-fence.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
            })

        distance = haversine(teacher_lat, teacher_lon, school_lat, school_lon)

        # Print detailed debug logs as requested
        print(f"Teacher Location: {teacher_lat}, {teacher_lon}")
        print(f"School Location: {school_lat}, {school_lon}")
        print(f"Calculated Distance: {distance} meters")

        allowed_radius = school.allowed_radius_meters if school.allowed_radius_meters is not None else 100

        if distance > allowed_radius:
            return render(request, "management/attendance_mark.html", {
                "error": "You are outside the school premises. Attendance cannot be marked.",
                "teachers": teachers,
                "schools": schools,
                "is_teacher": is_teacher,
                "today": today,
                "distance": int(distance),
                "max_distance": allowed_radius,
            })

        # Save status as Present (requirement 5)
        status = "PRESENT"

        # Save location info
        location_desc = f"GPS: {teacher_lat:.6f}, {teacher_lon:.6f}"

        attendance = Attendance.objects.create(
            teacher=teacher,
            school=school,
            attendance_date=today,
            attendance_time=timezone.now().time(),
            status=status,
            notes=notes,
            latitude=teacher_lat,
            longitude=teacher_lon,
            location=location_desc,
            distance_from_school=distance,
            created_at=timezone.now(),
        )

        return render(request, "management/attendance_mark.html", {
            "success": f"Attendance marked: '{attendance.get_status_display()}' at {school.name}.",
            "teachers": teachers,
            "schools": schools,
            "is_teacher": is_teacher,
            "today": today,
        })

    return render(request, "management/attendance_mark.html", {
        "teachers": teachers,
        "schools": schools,
        "is_teacher": is_teacher,
        "today": today,
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
        attendances = attendances.filter(status=status)
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
            present=Count("id", filter=Q(status="PRESENT")),
            absent=Count("id", filter=Q(status="ABSENT")),
            leave=Count("id", filter=Q(status="LEAVE")),
            cl=Count("id", filter=Q(status="CL")),
            half_day=Count("id", filter=Q(status="HALF_DAY")),
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
        "present_count": attendances.filter(status="PRESENT").count(),
        "absent_count": attendances.filter(status="ABSENT").count(),
        "leave_count": attendances.filter(status="LEAVE").count(),
        "cl_count": attendances.filter(status="CL").count(),
        "half_day_count": attendances.filter(status="HALF_DAY").count(),
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
            "Teacher", "School", "Date", "Time", "Status", "Created At",
            "Location", "Latitude", "Longitude", "Distance (m)", "Notes",
        ])
        for att in attendances:
            writer.writerow([
                att.teacher.full_name,
                att.school.name,
                att.attendance_date,
                att.attendance_time.strftime("%H:%M:%S") if att.attendance_time else "",
                att.get_status_display(),
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

    status_summary = attendances.values("status").annotate(count=Count("id"))
    teacher_summary = (
        attendances.values("teacher__first_name", "teacher__last_name")
        .annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status="PRESENT")),
            absent=Count("id", filter=Q(status="ABSENT")),
            leave=Count("id", filter=Q(status="LEAVE")),
            cl=Count("id", filter=Q(status="CL")),
            half_day=Count("id", filter=Q(status="HALF_DAY")),
        )
        .order_by("teacher__last_name")
    )

    status_map = dict(Attendance.StatusChoices.choices)
    status_summary_list = [
        {"status": s["status"], "label": status_map.get(s["status"], s["status"]), "count": s["count"]}
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
            "present_count": attendances.filter(status="PRESENT").count(),
            "absent_count": attendances.filter(status="ABSENT").count(),
            "leave_count": attendances.filter(status="LEAVE").count(),
            "cl_count": attendances.filter(status="CL").count(),
            "half_day_count": attendances.filter(status="HALF_DAY").count(),
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
        "status": attendance.status,
        "status_display": attendance.get_status_display(),
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

    status = payload.get("status", "PRESENT")
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

    if latitude is None or longitude is None:
        return JsonResponse({"error": "GPS coordinates are required to mark attendance."}, status=400)

    try:
        teacher_lat = float(latitude)
        teacher_lon = float(longitude)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid GPS coordinates structure."}, status=400)

    school_lat = school.school_latitude
    school_lon = school.school_longitude

    if school_lat is None or school_lon is None:
        return JsonResponse({"error": f"School '{school.name}' coordinates are not configured. Cannot verify geo-fence."}, status=400)

    distance = haversine(teacher_lat, teacher_lon, school_lat, school_lon)

    # Print detailed debug logs as requested
    print(f"Teacher Location: {teacher_lat}, {teacher_lon}")
    print(f"School Location: {school_lat}, {school_lon}")
    print(f"Calculated Distance: {distance} meters")

    allowed_radius = school.allowed_radius_meters if school.allowed_radius_meters is not None else 100

    if distance > allowed_radius:
        return JsonResponse(
            {"error": "You are outside the school premises. Attendance cannot be marked."},
            status=403,
        )

    # Force status to PRESENT when geo-fencing check succeeds
    status = "PRESENT"
    location_desc = f"GPS: {teacher_lat:.6f}, {teacher_lon:.6f}"

    attendance = Attendance.objects.create(
        teacher=teacher,
        school=school,
        attendance_date=today,
        attendance_time=timezone.now().time(),
        status=status,
        notes=payload.get("notes", ""),
        latitude=teacher_lat,
        longitude=teacher_lon,
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

    if not school_id or latitude is None or longitude is None:
        return JsonResponse({"error": "Missing school_id, latitude, or longitude"}, status=400)

    school = get_object_or_404(School, pk=school_id)

    if not school.school_latitude or not school.school_longitude:
        return JsonResponse({"error": f"School '{school.name}' has no GPS coordinates configured"}, status=400)

    distance = haversine(latitude, longitude, school.school_latitude, school.school_longitude)
    within = distance <= school.allowed_radius_meters

    return JsonResponse({
        "within": within,
        "distance": int(distance),
        "max_distance": school.allowed_radius_meters,
        "school": school.name,
    })
