"""
Tests for API endpoints called by Open EdX
"""
import json

from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from django.contrib.auth.models import User
from django.test import TestCase

from person.models import Permission, Student
from proctoring.models import (Course, Exam, EventSession,
                               InProgressEventSession)
from proctoring.api_edx_views import APIRoot, ExamViewSet


class APIRootTestCase(TestCase):
    def test_get(self):
        factory = APIRequestFactory()
        request = factory.get('/api/')
        view = APIRoot.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(type(data), dict)


class ExamViewSetTestCase(TestCase):
    def setUp(self):
        self.course = Course.create_by_course_run('org1/course1/run1')
        self.event = InProgressEventSession()
        self.event.testing_center = 'testing center'
        self.event.course = self.course
        self.event.course_event_id = '1'
        self.event.status = EventSession.IN_PROGRESS
        self.user = User.objects.create_user(
            'test',
            'test@test.com',
            'password'
        )
        self.event.proctor = self.user
        self.event.save()
        Permission.objects.create(
            user=self.user,
            object_type="*",
            object_id="*",
            role=Permission.ROLE_PROCTOR
        )
        student = Student.objects.create(
            sso_id=1,
            email='test@email.com',
            first_name='first_name',
            last_name='last_name'
        )
        exam = Exam()
        exam.exam_code = 'examCode'
        exam.organization = 'organization'
        exam.duration = 1
        exam.reviewed = True
        exam.reviewer_notes = 'reviewerNotes'
        exam.exam_password = 'examPassword'
        exam.exam_sponsor = 'examSponsor'
        exam.exam_name = 'examName'
        exam.ssi_product = 'ssiProduct'
        exam.first_name = 'firstName'
        exam.last_name = 'lastName'
        exam.username = 'username'
        exam.user_id = '1'
        exam.student = student
        exam.email = 'test@test.com'
        exam.exam_id = self.event.course_event_id
        exam.course = self.course
        exam.event = self.event
        exam.save()
        self.exam = exam

    def test_get_exam_by_session(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/exam_register/?session=%s' % self.event.hash_key)
        force_authenticate(request, user=self.user)
        view = ExamViewSet.as_view({'get': 'list'})

        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(type(data), list)
        self.assertTrue(len(data) > 0)

    def test_get_exam_by_without_session(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/exam_register/')
        force_authenticate(request, user=self.user)
        view = ExamViewSet.as_view({'get': 'list'})

        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 0)

    def test_get_exam_by_wrong_session(self):
        factory = APIRequestFactory()
        request = factory.get(
            '/api/exam_register/?session=%s' % "wrong_session")
        force_authenticate(request, user=self.user)
        view = ExamViewSet.as_view({'get': 'list'})

        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 0)

    @patch('proctoring.api_edx_views.send_ws_msg')
    def test_register_exam(self, send_ws_msg):
        factory = APIRequestFactory()
        exam_data = {
            "examCode": "newEamCode",
            "duration ": 2,
            "organization ": "newOrganization",
            "reviewedExam ": True,
            "reviewerNotes ": "newReviewerNotes",
            "examPassword ": "newExamPassword",
            "examSponsor ": "newExamSponsor",
            "examName ": "newExamName",
            "ssiProduct ": "newSsiProduct",
            "orgExtra": '''{
                "examStartDate": "2015-10-10 11:00",
                "examEndDate": "2015-10-10 15:00",
                "noOfStudents": 1,
                "examID": "wrong",
                "courseID": "wrong/course/id",
                "firstName": "first_name",
                "lastName": "last_name",
                "email": "test@test.com",
                "username": "test",
                "userID": "1"
            }'''
        }
        # send wrong data
        request = factory.post('/api/exam_register/',
                               data=exam_data,
                               )
        view = ExamViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # event non exists
        exam_data['orgExtra'] = '''{
            "examStartDate": "2015-10-10 11:00",
            "examEndDate": "2015-10-10 15:00",
            "noOfStudents": 1,
            "examID": "wrong",
            "courseID": "org1/course1/run1",
            "firstName": "first_name",
            "lastName": "last_name",
            "email": "test@test.com",
            "username": "test",
            "userID": "1"
        }'''
        request = factory.post(
            '/api/exam_register/',
            data=exam_data,
        )
        view = ExamViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # correct data
        exam_data['orgExtra'] = '''{
            "examStartDate": "2015-10-10 11:00",
            "examEndDate": "2015-10-10 15:00",
            "noOfStudents": 1,
            "examID": "1",
            "courseID": "org1/course1/run1",
            "firstName": "first_name",
            "lastName": "last_name",
            "email": "test@test.com",
            "username": "test",
            "userID": "1"
        }'''
        request = factory.post(
            '/api/exam_register/',
            data=exam_data,
        )
        view = ExamViewSet.as_view({'post': 'create'})
        response = view(request)
        response.render()
        data = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(type(data), dict)
        exam = Exam.objects.get(exam_code=exam_data['examCode'])
        self.assertDictContainsSubset({
            "examCode": exam.exam_code,
            "duration ": exam.duration,
            "organization ": exam.organization,
            "reviewedExam ": exam.reviewed,
            "reviewerNotes ": exam.reviewer_notes,
            "examPassword ": exam.exam_password,
            "examSponsor ": exam.exam_sponsor,
            "examName ": exam.exam_name,
            "ssiProduct ": exam.ssi_product,
        },
            exam_data
        )
        self.assertEqual(data['ID'], exam.generate_key())
        self.assertEqual(Exam.objects.count(), 2)
