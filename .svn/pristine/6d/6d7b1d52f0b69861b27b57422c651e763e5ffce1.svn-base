from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('active/<token>', views.ActiveView.as_view(), name='active'),
    path('', views.UserInfoView.as_view(), name='user'),
    path('order', views.UserOrderView.as_view(), name='order'),
    path('address', views.AddressView.as_view(), name='address'),
]
