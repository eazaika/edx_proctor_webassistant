"""
Tests for methods in model.py
"""
from django.test import TestCase
from django.contrib.auth.models import User

from person.models import Permission, Student
from proctoring.models import (Exam, Course, has_permission_to_course,
                               EventSession, InProgressEventSession)


class HasPermissionToCourseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )


class CourseTestCase(TestCase):
    def setUp(self):
        self.course = Course.create_by_course_run("org/course/run")

    def test_get_fill_course(self):
        result = self.course.get_full_course()
        self.assertEqual(result, "org/course/run")

    def test_get_by_course_run(self):
        course = Course.get_by_course_run("org/course/run")
        self.assertEqual(course, self.course)

    def test_get_course_data(self):
        # slashseparated course_id
        data = Course.get_course_data("org/course/run")
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 3)
        # plusseparated course_id
        data = Course.get_course_data("test:org+course+run")
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 3)


class HasPermissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )
        exam1 = _create_exam(1, 'org1/course1/run1')

    def test_has_permission_to_course(self):
        # wrong course_id
        self.assertFalse(has_permission_to_course(
            self.user,
            'org1course1run1'))
        # hasn't permissions
        self.assertFalse(has_permission_to_course(
            self.user,
            'org1/course1/run1'))
        # add permission
        perm1 = Permission.objects.create(
            user=self.user,
            object_id='org1/course1/run1',
            object_type=Permission.TYPE_COURSERUN,
            role=Permission.ROLE_PROCTOR
        )
        self.assertTrue(has_permission_to_course(
            self.user,
            'org1/course1/run1'))
        # instructor hasn't permissions
        self.assertFalse(has_permission_to_course(
            self.user,
            'org1/course1/run1',
            role=Permission.ROLE_INSTRUCTOR))

        perm1.delete()
        perm2 = Permission.objects.create(
            user=self.user,
            object_id='*',
            object_type='*',
            role=Permission.ROLE_PROCTOR
        )
        self.assertTrue(has_permission_to_course(
            self.user,
            'org1/course1/run1'))

        perm2.delete()

        self.user.is_superuser = True
        self.user.save()
        self.assertTrue(has_permission_to_course(
            self.user,
            'org1/course1/run1'))


class ExamByUserPermsManagerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )
        exam1 = _create_exam(1, 'org1/course1/run1')
        exam2 = _create_exam(2, 'org1/course2/run1')
        exam3 = _create_exam(3, 'org1/course2/run2')
        exam4 = _create_exam(4, 'org2/course1/run1')

    def test_by_user_perms(self):
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 0)
        perm1 = Permission.objects.create(
            user=self.user,
            object_id='org2/course1/run1',
            object_type=Permission.TYPE_COURSERUN
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 1)
        course_data = "/".join((exams[0].course.course_org,
                                exams[0].course.course_id,
                                exams[0].course.course_run))
        self.assertEqual(course_data, 'org2/course1/run1')
        perm2 = Permission.objects.create(
            user=self.user,
            object_id='org1/course2/run1',
            object_type=Permission.TYPE_COURSERUN
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 2)
        perm1.delete()
        perm3 = Permission.objects.create(
            user=self.user,
            object_id='org1/course2/run1',
            object_type=Permission.TYPE_COURSE
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 2)
        perm2.delete()
        perm3.delete()
        perm4 = Permission.objects.create(
            user=self.user,
            object_id='org1',
            object_type=Permission.TYPE_ORG
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 3)
        perm4.delete()
        perm5 = Permission.objects.create(
            user=self.user,
            object_id='*',
            object_type=Permission.TYPE_ORG
        )
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 4)

        Permission.objects.filter(user=self.user).delete()
        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), 0)

        self.user.is_superuser = True
        self.user.save()

        exams = Exam.objects.by_user_perms(self.user)
        self.assertEqual(len(exams), Exam.objects.count())


class ExamTestCase(TestCase):
    def setUp(self):
        self.exam = _create_exam(1, 'org/course/run')

    def test_generate_key(self):
        result = self.exam.generate_key()
        self.assertEqual(type(result), str)
        self.assertRegexpMatches(result, r"([a-fA-F\d]{32})")


class EventSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test1', 'test1@test.com', 'testpassword'
        )
        exam1 = _create_exam(1, 'org1/course1/run1')

    def test_post_save(self):
        event = InProgressEventSession()
        event.testing_center = "test center"
        event.course = Course.create_by_course_run('org/course/run')
        event.course_event_id = 'id'
        event.proctor = self.user
        event.save()
        event = EventSession.objects.get(pk=event.pk)
        self.assertEqual(type(event.hash_key), str)
        self.assertRegexpMatches(event.hash_key, r"([a-fA-F\d]{32})")

    def test_update_queryset_with_permissions(self):
        perm1 = Permission.objects.create(
            user=self.user,
            object_id='org1/course1/run1',
            object_type=Permission.TYPE_COURSERUN,
            role=Permission.ROLE_PROCTOR
        )
        qs = EventSession.update_queryset_with_permissions(
            EventSession.objects.all(), self.user
        )
        self.assertNotEqual(qs, EventSession.objects.all())

        perm1.delete()

        perm2 = Permission.objects.create(
            user=self.user,
            object_id='org1/course1/run1',
            object_type=Permission.TYPE_COURSERUN,
            role=Permission.ROLE_INSTRUCTOR
        )
        qs = EventSession.update_queryset_with_permissions(
            EventSession.objects.all(), self.user
        )
        self.assertNotEqual(qs, EventSession.objects.all())

        perm2.delete()

        perm3 = Permission.objects.create(
            user=self.user,
            object_id='*',
            object_type='*',
            role=Permission.ROLE_PROCTOR
        )
        qs = EventSession.update_queryset_with_permissions(
            EventSession.objects.all(), self.user
        )
        self.assertNotEqual(qs, EventSession.objects.filter(proctor=self.user))


def _create_exam(id, course_id):
    student = Student.objects.create(
        sso_id=1,
        email='test@test.com',
        first_name='Test',
        last_name='Test'
    )

    exam = Exam()
    exam.exam_code = 'examCode_%s' % id
    exam.duration = 1
    exam.reviewed = True
    exam.reviewer_notes = 'reviewerNotes_%s' % id
    exam.exam_password = 'examPassword_%s' % id
    exam.exam_sponsor = 'examSponsor_%s' % id
    exam.exam_name = 'examName_%s' % id
    exam.ssi_product = 'ssiProduct_%s' % id
    exam.first_name = 'firstName_%s' % id
    exam.last_name = 'lastName_%s' % id,
    exam.course = Course.create_by_course_run(course_id)
    exam.exam_id = '1'
    exam.email = 'test@test.com'
    exam.student = student
    exam.save()
    return exam
