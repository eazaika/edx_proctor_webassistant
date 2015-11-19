import json
from datetime import datetime
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status, mixins
from rest_framework.authentication import BasicAuthentication, \
    TokenAuthentication
from api.web_soket_methods import send_ws_msg
from models import Exam, EventSession
from serializers import EventSessionSerializer
from edx_api import start_exam_request, poll_status_request, \
    send_review_request, get_proctored_exams
from api.auth import CsrfExemptSessionAuthentication, SsoTokenAuthentication


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def start_exam(request, attempt_code):
    exam = get_object_or_404(Exam, exam_code=attempt_code)

    response = start_exam_request(exam.exam_code)
    if response.status_code == 200:
        exam.exam_status = exam.STARTED
        exam.proctor = request.user
        exam.save()
        data = {
            'hash': exam.generate_key(),
            'proctor': exam.proctor.username,
            'status': "OK"
        }
        send_ws_msg(data)
    else:
        data = {'error': 'Edx response error. See logs'}
    return Response(data=data, status=response.status_code)


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def poll_status(request, attempt_code):
    exam = get_object_or_404(Exam, exam_code=attempt_code)
    response = poll_status_request(exam.exam_code)
    status = json.loads(response.content)
    data = {
        'hash': exam.generate_key(),
        'status': status.get('status')
    }
    send_ws_msg(data)
    return Response(data=data, status=response.status_code)


class EventSessionViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """
    Event managment API

    For **create** send `testing_center`,`course_id`,`course_event_id`
    Other fields filling automaticaly

    You can **update** only `status` and `notify` fields
    """
    serializer_class = EventSessionSerializer
    queryset = EventSession.objects.all()

    def create(self, request, *args, **kwargs):
        fields_for_create = ['testing_center', 'course_id', 'course_event_id']
        data = {}
        for field in fields_for_create:
            data[field] = request.data.get(field)
        data['proctor'] = request.user.pk
        data['status'] = EventSession.IN_PROGRESS
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_ws_msg(data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}

    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        fields_for_update = ['status', 'notify']
        data = {}

        for field in fields_for_update:
            data[field] = request.data.get(field)
        change_end_date = instance.status == EventSession.IN_PROGRESS and \
                          data.get('status') == EventSession.FINISHED

        serializer = self.get_serializer(instance, data=data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if change_end_date:
            event_session = EventSession.objects.get(pk=instance.pk)
            event_session.end_date = datetime.now()
            event_session.save()
            serializer = self.get_serializer(event_session)
        return Response(serializer.data)


class Review(APIView):
    authentication_classes = (
        SsoTokenAuthentication, CsrfExemptSessionAuthentication,
        BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Request example:

        `{"attempt_code":"029288A9-9198-4C99-9D3F-E589695CF5D7"}`

        """
        passing_review_status = ['Clean', 'Rules Violation']
        failing_review_status = ['Not Reviewed', 'Suspicious']
        exam = get_object_or_404(Exam,
                                 exam_code=request.data.get('attempt_code'))

        review_payload = {
            "examDate": "",
            "examProcessingStatus": "Review Completed",
            "examTakerEmail": " ",
            "examTakerFirstName": "John",
            "examTakerLastName": "Doe",
            "keySetVersion": "",
            "examApiData": {
                "duration": exam.duration,
                "examCode": exam.exam_code,
                "examName": exam.exam_name,
                "examPassword": exam.exam_password,
                "examSponsor": exam.exam_sponsor,
                "examUrl": "http://localhost:8000/api/edx_proctoring/proctoring_launch_callback/start_exam/4d07a01a-1502-422e-b943-93ac04dc6ced",
                "orgExtra": {
                    "courseID": exam.course_id,
                    "examEndDate": exam.exam_end_date,
                    "examID": exam.exam_id,
                    "examStartDate": exam.exam_start_date,
                    "noOfStudents": exam.no_of_students
                },
                "organization": exam.organization,
                "reviewedExam": exam.reviewed_exam,
                "reviewerNotes": exam.reviewer_notes,
                "ssiProduct": "rp-now"
            },
            "overAllComments": "",
            "reviewStatus": passing_review_status[0],
            "userPhotoBase64String": "",
            "videoReviewLink": "",
            "examMetaData": {
                "examCode": request.data.get('attempt_code'),
                "examName": exam.exam_name,
                "examSponsor": exam.exam_sponsor,
                "organization": exam.organization,
                "reviewedExam": "True",
                "reviewerNotes": "Closed Book",
                "simulatedExam": "False",
                "ssiExamToken": "",
                "ssiProduct": "rp-now",
                "ssiRecordLocator": exam.generate_key()
            },
            "desktopComments": [
                {
                    "comments": "Browsing other websites",
                    "duration": 88,
                    "eventFinish": 88,
                    "eventStart": 12,
                    "eventStatus": "Suspicious"
                },
            ],
            "webCamComments": [
                {
                    "comments": "Photo ID not provided",
                    "duration": 796,
                    "eventFinish": 796,
                    "eventStart": 0,
                    "eventStatus": "Suspicious"
                }
            ]
        }

        response = send_review_request(review_payload)
        data = {
            'hash': exam.generate_key(),
            'status': ''
        }
        if response.status_code == 200:
            data['status'] = 'review_was_sent'
        else:
            data['status'] = 'review_send_failed'

        return Response(data=data,
                        status=response.status_code)


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_exams_proctored(request):

    return get_proctored_exams()


@api_view(['GET'])
@authentication_classes((SsoTokenAuthentication,))
@permission_classes((IsAuthenticated,))
def bulk_start_exams(request, exam_codes):
    """
    Start list of exams by exam codes.

    :param request:
    :param exam_codes: comaseparated list of exam codes
    :return:
    """

    exam_list = Exam.objects.filter(exam_code__in=exam_codes)
    response = bulk_start_exams_request(exam_list)
    status = json.loads(response.content)
    data = {
        'status': status.get('status')
    }
    send_ws_msg(data)
    return Response(data=data, status=response.status_code)
