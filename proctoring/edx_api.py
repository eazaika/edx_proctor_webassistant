# -*- coding: utf-8 -*-
"""
There are requests to edX API
See https://github.com/edx/edx-proctoring/blob/master/edx_proctoring/api.py
"""
import json
import requests

from bs4 import BeautifulSoup

from django.conf import settings

from edx_proctor_webassistant.utils import date_handler
from journaling.models import Journaling


def start_exam_request(attempt_code):
    """
    Call edX callback on exam start
    :param attempt_code:
    :return: Response
    """
    return _journaling_request(
        'get',
        "api/edx_proctoring/proctoring_launch_callback/start_exam/" + attempt_code
    )


def stop_exam_request(_id, action, user_id):
    """
    Call edX stop exam endpoint
    :param _id: str
    :param action: str
    :param user_id: str
    :return: Response
    """
    return _journaling_request(
        'put',
        "api/edx_proctoring/v1/proctored_exam/attempt/" + _id,
        json.dumps({'action': action, 'user_id': user_id, 'initiator': 'proctor'}),
        {'Content-Type': 'application/json'}
    )


def bulk_update_exams_statuses(attempts):
    """
    Call edX endpoint to bulk update exams statuses
    :return: Response
    """
    return _journaling_request(
        'post',
        'api/extended/edx_proctoring/attempts_bulk_update/',
        json.dumps({'attempts': attempts}),
        {'Content-Type': 'application/json', 'X-Edx-Api-Key': settings.EDX_API_KEY}
    )


def poll_status_request(codes):
    """
    Get list of exam statuses from edX
    :param codes: list
    :return: List of Responses
    """
    if isinstance(codes, list):
        res = []
        for code in codes:
            ret = poll_status(code)
            if ret.status_code == 200:
                payload = ret.json()
                payload['attempt_code'] = code
                res.append(payload)
        return res
    else:
        return []


def poll_statuses_attempts_request(codes):
    """
    Get list of exam statuses from edX
    :param codes: list
    :return: List of Responses
    """
    if isinstance(codes, list):
        ret = poll_statuses_attempts(codes)
        if ret.status_code == 200:
            return ret.json()
    return {}


def poll_status(code):
    return requests.get(
        settings.EDX_URL + "api/edx_proctoring/proctoring_poll_status/" + code,
    )


def poll_statuses_attempts(codes_list):
    return requests.post(
        settings.EDX_URL + "api/extended/edx_proctoring/proctoring_poll_statuses_attempts/",
        json={"attempts": codes_list}
    )


def send_review_request(payload):
    """
    Send review to edX after exam finished
    :param payload: dict
    :return: Response
    """
    return _journaling_request(
        'post',
        "api/edx_proctoring/proctoring_review_callback/",
        json.dumps(payload, default=date_handler),
    )


def get_proctored_exams_request(page=1):
    """
    Get list of courses wich contains proctored exams
    Api extension must be installed for you OpenEDX
    See https://github.com/raccoongang/open_edx_api_extension
    :return: Response
    next for paging responce - if number of courses more than 10
    """
    api_point = 'api/extended/courses/proctored'
    if page != 1:
        api_point = '{0}?page={1}'.format(api_point, page)

    resp = _journaling_request(
        'get',
        api_point,
        {"proctoring_system": "WEB_ASSISTANT"},
        headers={'X-Edx-Api-Key': settings.EDX_API_KEY}
    )
    return resp


def bulk_start_exams_request(exam_list):
    """
    Endpoint for start list of exams
    :param exam_list: list
    :return: List of Responses
    """
    result = []
    url = "api/edx_proctoring/proctoring_launch_callback/start_exam/%s"
    for exam in exam_list:
        response = _journaling_request(
            'get', url % str(exam.exam_code),
        )
        if response.status_code == 200:
            result.append(exam)
    return result


def _journaling_request(request_type, url, data=None, headers=None):
    """
    Method wich journaling all requests and responses for edX
    :param request_type: get, post or put
    :param url: str
    :param data: dict
    :param headers: dict
    :return: Response
    """
    if request_type == "post":
        response = requests.post(
            settings.EDX_URL + url,
            data=data,
            headers=headers
        )
    elif request_type == "get":
        if data:
            response = requests.get(
                settings.EDX_URL + url,
                params=data,
                headers=headers
            )
        else:
            response = requests.get(
                settings.EDX_URL + url,
                headers=headers
            )
    elif request_type == "put":
        response = requests.put(
            settings.EDX_URL + url,
            data=data,
            headers=headers
        )
    else:
        raise Exception('Invalid request_type', request_type)
    try:
        result = response.json()
    except ValueError:
        soup = BeautifulSoup(str(response.content))
        h1 = soup.find('h1')
        res_list = []
        if h1:
            res_list.append(h1.get_text())
        pre = soup.find('pre', {"class": "exception_value"})
        if pre:
            res_list.append(pre.get_text())
        if res_list:
            result = "\n ".join(res_list)
        else:
            result = str(response.content)
    try:
        Journaling.objects.create(
            journaling_type=Journaling.EDX_API_CALL,
            note="""
Call url:%s
Sent data: %s
Response status: %s
Response content: %s
            """ % (
                url,
                str(data).encode('utf-8'),
                str(response.status_code),
                str(result)
            )
        )
    except:
        pass
    return response
