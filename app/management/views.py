import json
import os
import subprocess
import glob
import io

from django.conf import settings
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import AttendanceForm, CourseForm, SchoolForm, TeacherForm
from .models import Attendance, Course, School, Teacher


def dashboard(request):
    return render(
        request,
        "management/dashboard.html",
        {
            "teacher_count": Teacher.objects.count(),
            "school_count": School.objects.count(),
            "course_count": Course.objects.count(),
            "attendance_count": Attendance.objects.count(),
            "upcoming_attendances": Attendance.objects.select_related(
                "teacher",
                "school",
                "course",
            )[:8],
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


def attendance_list(request):
    attendances = Attendance.objects.select_related("teacher", "school", "course")
    return render(
        request,
        "management/attendance_list.html",
        {"attendances": attendances},
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
        "course": course_to_dict(attendance.course),
        "weekday": attendance.weekday,
        "weekday_display": attendance.get_weekday_display(),
        "start_time": attendance.start_time.strftime("%H:%M"),
        "end_time": attendance.end_time.strftime("%H:%M"),
        "room": attendance.room,
        "location": attendance.location,
        "start_date": attendance.start_date.isoformat() if attendance.start_date else None,
        "end_date": attendance.end_date.isoformat() if attendance.end_date else None,
        "notes": attendance.notes,
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

    required = ["teacher_id", "school_id", "course_id", "weekday", "start_time", "end_time"]
    missing = [field for field in required if not payload.get(field)]

    if missing:
        return JsonResponse({"error": "Missing fields", "fields": missing}, status=400)

    teacher = get_object_or_404(Teacher, pk=payload["teacher_id"])
    school = get_object_or_404(School, pk=payload["school_id"])
    course = get_object_or_404(Course, pk=payload["course_id"])

    attendance = Attendance.objects.create(
        teacher=teacher,
        school=school,
        course=course,
        weekday=payload["weekday"],
        start_time=payload["start_time"],
        end_time=payload["end_time"],
        room=payload.get("room", ""),
        location=payload.get("location", ""),
        start_date=payload.get("start_date") or None,
        end_date=payload.get("end_date") or None,
        notes=payload.get("notes", ""),
    )

    return JsonResponse(attendance_to_dict(attendance), status=201)


@csrf_exempt
@require_http_methods(["POST"])
def api_manage_update(request):
    # Retrieve security token from headers or Authorization header
    provided_token = request.headers.get("X-Management-Token")
    if not provided_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            provided_token = auth_header.split(" ", 1)[1]

    # Or retrieve from request body / GET param
    if not provided_token:
        try:
            payload = json.loads(request.body or "{}")
            provided_token = payload.get("token")
        except Exception:
            pass

    expected_token = os.environ.get("MANAGEMENT_API_TOKEN")

    if not expected_token:
        return JsonResponse({
            "status": "error",
            "message": "Management token is not configured on the server. Please set the MANAGEMENT_API_TOKEN environment variable."
        }, status=500)

    if provided_token != expected_token:
        return JsonResponse({
            "status": "error",
            "message": "Unauthorized"
        }, status=403)

    log = []

    # 1. git pull
    try:
        log.append("Executing git pull...")
        res = subprocess.run(
            ["git", "pull"],
            cwd=str(settings.BASE_DIR),
            capture_output=True,
            text=True,
            check=True
        )
        log.append(f"git pull output: {res.stdout.strip()}")
        if res.stderr:
            log.append(f"git pull stderr: {res.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        log.append(f"git pull failed: {e.stderr or str(e)}")
        return JsonResponse({
            "status": "error",
            "message": "Git pull failed",
            "log": log
        }, status=500)
    except Exception as e:
        log.append(f"git pull error: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Git pull encountered an error: {str(e)}",
            "log": log
        }, status=500)

    # 2. makemigrations
    try:
        log.append("Executing makemigrations...")
        out = io.StringIO()
        call_command("makemigrations", stdout=out, stderr=out)
        log.append(f"makemigrations output: {out.getvalue().strip()}")
    except Exception as e:
        log.append(f"makemigrations error: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"makemigrations failed: {str(e)}",
            "log": log
        }, status=500)

    # 3. migrate
    try:
        log.append("Executing migrate...")
        out = io.StringIO()
        call_command("migrate", stdout=out, stderr=out)
        log.append(f"migrate output: {out.getvalue().strip()}")
    except Exception as e:
        log.append(f"migrate error: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"migrate failed: {str(e)}",
            "log": log
        }, status=500)

    # 4. Restart server (touch PythonAnywhere wsgi files or local config/wsgi.py)
    try:
        log.append("Triggering server reload...")
        reloaded_files = []
        wsgi_files = glob.glob("/var/www/*_wsgi.py")
        for wsgi_file in wsgi_files:
            os.utime(wsgi_file, None)
            reloaded_files.append(wsgi_file)

        local_wsgi = settings.BASE_DIR / "config" / "wsgi.py"
        if local_wsgi.exists():
            os.utime(str(local_wsgi), None)
            reloaded_files.append(str(local_wsgi))

        log.append(f"Reloaded WSGI configuration files: {reloaded_files}")
    except Exception as e:
        log.append(f"Server reload error: {str(e)}")

    return JsonResponse({
        "status": "success",
        "message": "Git pull, migrations, and server restart triggered successfully.",
        "log": log
    })
