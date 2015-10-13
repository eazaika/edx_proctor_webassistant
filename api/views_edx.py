from rest_framework.reverse import reverse
from rest_framework import viewsets, status
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from serializers import ExamSerializer
from models import Exam


class APIRoot(APIView):
    """API Root for accounts module"""

    def get(self, request):
        result = {
            "exam_register": reverse('exam-register-list', request=request),
            "start_exam": reverse(
                'start_exam',
                request=request, args=('attempt_code',)
            ),
        }
        return Response(result)


class ExamViewSet(viewsets.ModelViewSet):
    """
    This viewset regiter edx's exam on proctoring service and return generated code
    Required parameters:
    ```
    examCode,
    organization,
    duration,
    reviewedExam,
    reviewerNotes,
    examPassword,
    examSponsor,
    examName,
    ssiProduct,
    orgExtra
    ```

    orgExtra contain json like this:

        {
            "examStartDate": "2015-10-10 11:00",
            "examEndDate": "2015-10-10 15:00",
            "noOfStudents": 1,
            "examId": "id",
            "courseId": "course_id",
            "firstName": "first_name",
            "lastName": "last_name"
        }

    """
    serializer_class = ExamSerializer
    queryset = Exam.objects.all()

    # @csrf_exempt
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'ID': serializer.instance.generate_key()},
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            return {}