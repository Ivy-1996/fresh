from django.urls import path
from . import views



app_name = 'user'

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('active/?P<token>.*?', views.ActiveView.as_view(), name='active'),
]