from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.home,           name='home'),
    path('upload/',                       views.upload,         name='upload'),
    path('result/<str:detection_id>/',    views.result,         name='result'),
    path('download/<str:detection_id>/',  views.download_pdf,   name='download_pdf'),
    path('webcam/',                       views.webcam,         name='webcam'),
    path('chatbot/',                      views.chatbot,        name='chatbot'),
    path('dashboard/',                    views.dashboard,      name='dashboard'),
    path('history/',                      views.history,        name='history'),
    path('api/chat/',                     views.chat_api,       name='chat_api'),
    path('api/webcam-predict/',           views.webcam_predict, name='webcam_predict'),
]
