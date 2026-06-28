from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from management.models import School, Teacher, Attendance, SchoolSettings
from management.utils import haversine


class GeofenceTestCase(TestCase):
    def setUp(self):
        # Delete default SchoolSettings created by migrations to avoid interfering with school-specific tests
        SchoolSettings.objects.all().delete()

        # Create a test school in Shivajinagar, Pune
        self.school = School.objects.create(
            name="Greenwood High",
            school_latitude=18.52043,
            school_longitude=73.856743,
            allowed_radius_meters=100
        )
        
        # Create a user & teacher profile linked to this school
        self.user = User.objects.create_user(username="teacher_john", password="password123")
        self.teacher = Teacher.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            school=self.school,
            active=True
        )

    def test_haversine_distance_calculation(self):
        # Greenwood School: 18.52043, 73.856743
        # Close coordinates: 18.52045, 73.856750 (approx 3 meters away)
        dist_close = haversine(18.52043, 73.856743, 18.52045, 73.856750)
        self.assertIsNotNone(dist_close)
        self.assertLess(dist_close, 10)
        
        # Far coordinates: 18.52843, 73.856743 (approx 890 meters away)
        dist_far = haversine(18.52043, 73.856743, 18.52843, 73.856743)
        self.assertIsNotNone(dist_far)
        self.assertGreater(dist_far, 800)

    def test_attendance_model_save_and_weekday(self):
        # Use a fixed date for the test: 2026-06-20 (Saturday)
        test_date = date(2026, 6, 20)
        
        attendance = Attendance.objects.create(
            teacher=self.teacher,
            school=self.school,
            attendance_date=test_date,
            attendance_status="PRESENT",
            standard_class="10th Grade",
            latitude=18.52043,
            longitude=73.856743,
            distance_from_school=0
        )
        
        # Ensure weekday is auto-calculated and matches 'SAT' (Saturday)
        self.assertEqual(attendance.weekday, "SAT")
        self.assertEqual(attendance.get_attendance_status_display(), "Present")
        self.assertEqual(attendance.standard_class, "10th Grade")
        self.assertIsNotNone(attendance.created_at)
        self.assertIsNotNone(attendance.attendance_time)

    def test_mark_attendance_inside_radius(self):
        self.client.login(username="teacher_john", password="password123")
        
        # Coordinates approx 5 meters away (18.52043, 73.856743 is Greenwood High)
        response = self.client.post("/attendances/mark/", {
            "status": "PRESENT",
            "latitude": "18.52045",
            "longitude": "73.856750",
            "standard_class": "10th Grade"
        })
        
        # Assert database entry was created
        attendance = Attendance.objects.filter(teacher=self.teacher).first()
        self.assertIsNotNone(attendance)
        self.assertEqual(attendance.attendance_status, "PRESENT")
        self.assertEqual(attendance.standard_class, "10th Grade")
        self.assertLess(attendance.distance_from_school, 10)
        self.assertContains(response, "Attendance marked")

    def test_mark_attendance_outside_radius(self):
        self.client.login(username="teacher_john", password="password123")
        
        # Coordinates far away (Pune Airport - approx 8.5 km away)
        response = self.client.post("/attendances/mark/", {
            "status": "PRESENT",
            "latitude": "18.5793",
            "longitude": "73.9089",
            "standard_class": "10th Grade"
        })
        
        # Assert rejected and database entry not created
        attendance = Attendance.objects.filter(teacher=self.teacher).first()
        self.assertIsNone(attendance)
        self.assertContains(response, "You are outside the school campus. Attendance can only be marked when you are near the school.")

    def test_mark_attendance_missing_coords(self):
        self.client.login(username="teacher_john", password="password123")
        
        response = self.client.post("/attendances/mark/", {
            "status": "PRESENT",
            "latitude": "",
            "longitude": "",
            "standard_class": "10th Grade"
        })
        
        attendance = Attendance.objects.filter(teacher=self.teacher).first()
        self.assertIsNone(attendance)
        self.assertContains(response, "GPS coordinates are required to submit attendance.")

    def test_api_attendance_create_inside(self):
        import json
        payload = {
            "teacher_id": self.teacher.id,
            "school_id": self.school.id,
            "latitude": 18.52045,
            "longitude": 73.856750,
            "standard_class": "10th Grade"
        }
        
        response = self.client.post(
            "/api/attendances/create/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "PRESENT")
        self.assertEqual(data["standard_class"], "10th Grade")
        
        attendance = Attendance.objects.filter(teacher=self.teacher).first()
        self.assertIsNotNone(attendance)
        self.assertEqual(attendance.standard_class, "10th Grade")

    def test_api_attendance_create_outside(self):
        import json
        payload = {
            "teacher_id": self.teacher.id,
            "school_id": self.school.id,
            "latitude": 18.5793,
            "longitude": 73.9089,
            "standard_class": "10th Grade"
        }
        
        response = self.client.post(
            "/api/attendances/create/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "You are outside the school campus. Attendance can only be marked when you are near the school.")
        
        attendance = Attendance.objects.filter(teacher=self.teacher).first()
        self.assertIsNone(attendance)

    def test_api_attendance_create_missing_coords(self):
        import json
        payload = {
            "teacher_id": self.teacher.id,
            "school_id": self.school.id,
            "standard_class": "10th Grade"
        }
        
        response = self.client.post(
            "/api/attendances/create/",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data["error"], "GPS coordinates are required to mark attendance.")
