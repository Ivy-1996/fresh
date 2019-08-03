from django.urls import path, re_path
from . import views


app_name = 'goods'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'^goods/(?P<pk>\d+)$', views.DetailView.as_view(), name='detail')
]
