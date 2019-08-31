from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('place', views.OrderPlaceView.as_view(), name='place'),
    path('commit', views.OrderCommitView.as_view(), name='commit'),
    path('pay', views.OrderPayView.as_view(), name='pay'),
    path('check', views.OrderCheckView.as_view(), name='check'),
]
