import os
import logging
import pandas as pd

from django.core.files.storage import default_storage
from django.template.loader import render_to_string

from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from artivatic_ai.home.tasks import send_email_content_type

from artivatic_ai.common.models import Document
from artivatic_ai.home.models import UserEmail


logger = logging.getLogger(__name__)


def index(request):
    context = {}
    logger.info('Welcome to home!')
    return render(request, 'home/index.html', context)


@api_view(['POST'])
def send_email_api(request):
    """
    sending single mail
    :param request:
    :return: response
    """
    data = request.data

    send_mail_fuc(data)
    
    return Response(
        {"status": "Ok"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_email_bulk_upload_api(request):
    """
    bulk upload of send mail from csv file
    :param request:
    :return: response
    """
    file = request.FILES.get('file')    
    file_title = file.name
    path = settings.TEMP_PATH + file_title
    extension = file_title.split(".")[-1].lower()
    file_name = default_storage.save(path, file)

    file_path = os.path.join(settings.BASE_DIR, file_name)

    print(file_title, extension, file_name)

    if extension in ['csv']:
        email_list = pd.read_csv(file_path)
        for idx, row in email_list.iterrows():
            data = row.to_dict()
            send_mail_fuc(data)
        
        return Response(
            {"status": "Ok"}, status=status.HTTP_200_OK)
    return Response({
        'error': 'File not supported.'
    }, status-status.HTTP_400_BAD_REQUEST)


def send_mail_fuc(data):
    subject = 'test mail'
    message = render_to_string(
        'email/email_content.html'
    )
    to = data.get('email').split(',')
    if data.get('bcc_email'):
        bcc_email = data.get('bcc_email').split(',')
    else:
        bcc_email = []
    if data.get('cc_email'):
        cc_email = data.get('cc_email').split(',')
    else:
        cc_email = []

    email_data = set(to + bcc_email + cc_email)

    for each in email_data:
        try:
            user_email = UserEmail.objects.get(email=each)
            user_email.update()
        except UserEmail.DoesNotExist:
            UserEmail.objects.create(email=each)

    send_email_content_type(subject, message, to, bcc_email, cc_email)
