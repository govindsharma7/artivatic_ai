import logging
import urllib

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab

from django.contrib.auth.models import User
from django.template.loader import render_to_string

from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail, EmailMultiAlternatives



logger = logging.getLogger(__name__)


@task(name="send emails")
def send_emails(subject, message, recipient_list):
    default_from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, default_from_email, recipient_list)
    return True


@task(name="send content type emails")
def send_email_content_type(email_subject, message, user_email, bcc_email, cc_email):
    default_from_email = settings.EMAIL_HOST_USER
    if type(user_email) != list:
        user_email = [user_email]
    if type(bcc_email) != list:
        user_email = [bcc_email]
    if type(cc_email) != list:
        user_email = [cc_email]
    msg = EmailMultiAlternatives(
        subject=email_subject, body=message,
        from_email=default_from_email, to=user_email,
        bcc=bcc_email, cc=cc_email
    )
    recipient_list = user_email + bcc_email + cc_email
    logger.info('mail to : ' + str(recipient_list) + ' at ' + str(datetime.now()))
    msg.attach_alternative(message, "text/html")
    result = msg.send()

    return result


@periodic_task(run_every=(crontab(minute='*/30')), name="statistics", ignore_result=True)
def statistics():
    '''
    Curl Request:
    curl -XGET "http://localhost:9200/_search" -H 'Content-Type: application/json' -d'
    {
        "query": {
            "range" : {
                "timestamp" : {
                    "time_zone": "+01:00", 
                    "gte": "2019-11-01 00:00:00", 
                    "lte": "now" 
                }
            }
        }
    }'
    '''
    uri = 'http://localhost:9200/_search'
    query = {
        "query": {
            "range" : {
                "timestamp" : {
                    "time_zone": "+01:00", 
                    "gte": "2019-11-01 00:00:00", 
                    "lte": "now" 
                }
            }
        }
    }
    resp = requests.get(uri, data=query, headers='content-type:application/json')
    try:
        resp_text = json.loads(resp.text)
    except:
        resp_text = resp.text

    # f = urllib.urlopen('localhost:9600/_node/stats/?pretty')
    # myfile = f.read()
    
    subject = 'test mail'
    message = render_to_string(
        'email/email_content_data.html', {'data': resp_text}
    )
    to = User.objects.filter(is_superuser=True).values_list(
        'email', flat=True)
    bcc_email = []
    cc_email = []
    send_email_content_type(subject, message, to, bcc_email, cc_email)
