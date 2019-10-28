from django.urls import path
from artivatic_ai.home import views as vw


urlpatterns = [
    path('', vw.index, name='index'),
    path('send_email', vw.send_email_api),
    path('bulk/send_email', vw.send_email_bulk_upload_api),
]
