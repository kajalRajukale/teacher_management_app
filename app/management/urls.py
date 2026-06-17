from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/new/", views.teacher_create, name="teacher_create"),
    path("teachers/<int:pk>/edit/", views.teacher_update, name="teacher_update"),
    path("teachers/<int:pk>/delete/", views.teacher_delete, name="teacher_delete"),

    path("schools/", views.school_list, name="school_list"),
    path("schools/new/", views.school_create, name="school_create"),
    path("schools/<int:pk>/edit/", views.school_update, name="school_update"),
    path("schools/<int:pk>/delete/", views.school_delete, name="school_delete"),

    path("courses/", views.course_list, name="course_list"),
    path("courses/new/", views.course_create, name="course_create"),
    path("courses/<int:pk>/edit/", views.course_update, name="course_update"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),

    path("attendances/", views.attendance_list, name="attendance_list"),
    path("attendances/new/", views.attendance_create, name="attendance_create"),
    path("attendances/<int:pk>/edit/", views.attendance_update, name="attendance_update"),
    path("attendances/<int:pk>/delete/", views.attendance_delete, name="attendance_delete"),

    path("api/teachers/", views.api_teacher_list, name="api_teacher_list"),
    path("api/teachers/create/", views.api_teacher_create, name="api_teacher_create"),
    path("api/teachers/<int:pk>/", views.api_teacher_detail, name="api_teacher_detail"),
    path("api/teachers/<int:pk>/update/", views.api_teacher_update, name="api_teacher_update"),
    path("api/teachers/<int:pk>/delete/", views.api_teacher_delete, name="api_teacher_delete"),

    path("api/schools/", views.api_school_list, name="api_school_list"),
    path("api/courses/", views.api_course_list, name="api_course_list"),
    path("api/attendances/", views.api_attendance_list, name="api_attendance_list"),
    path("api/attendances/create/", views.api_attendance_create, name="api_attendance_create"),
]
