from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views import View
from django.conf import settings
from apps.user.models import User
import re
from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
import time
from celery_tasks.task import send_register_mail


# Create your views here.

class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整!'})

        allow = request.POST.get('allow')
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议!'})

        reg = "[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?"
        if not re.match(reg, email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法!'})

        if User.objects.filter(username=username):
            return render(request, 'register.html', {'errmsg': '用户名已被注册!'})

        if User.objects.filter(email=email):
            return render(request, 'register.html', {'errmsg': '邮箱已被注册!'})

        user = User.objects.create_user(username, email, password)
        user.is_active = False
        user.save()

        serializer = Serializer(settings.SECRET_KEY)
        data = {'id': user.id, 'time': time.time()}
        token = serializer.dumps(data).decode()

        send_register_mail(email, username, token)

        return redirect(reverse('goods:index'))


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')


class ActiveView(View):
    def get(self, request, token: str):
        serializer = Serializer(settings.SECRET_KEY)
        try:
            data = serializer.loads(token.encode())
            user_id = data.get('id')
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            return redirect(reverse('user:login'))
        except BadSignature:
            return HttpResponse('错误的请求链接!', status=401)
