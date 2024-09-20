from django.urls import path
from . import views

app_name = 'expression'
urlpatterns = [
    path('', views.main, name='main'),
    path('user_form/', views.user_form, name= 'user_form'),
    path('<int:id>/details', views.details, name='details')
]