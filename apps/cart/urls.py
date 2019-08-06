
from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [
    path('add', views.CartAddView.as_view(), name='add'),
]