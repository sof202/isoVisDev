from django.urls import path
from . import views
from .views import transcript_identify 

app_name = 'expression'
urlpatterns = [
    path('', views.main, name='main'),
    path('user_form/', views.user_form, name= 'user_form'),
    path('transcript/', transcript_identify, name= 'transcript'),
    path('<int:id>/details', views.details, name='details')
]