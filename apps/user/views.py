from django.shortcuts import render, redirect, reverse, HttpResponse
from django.views import View
from django.conf import settings
from django_redis import get_redis_connection
from django.contrib.auth import authenticate, login, logout
from apps.user.models import User, Address
from apps.goods.models import GoodsSKU
import re
from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
import time
from celery_tasks.task import send_register_mail
from utils.mixin import LoginRequredMixIn


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

        return redirect(reverse('user:login'))


class LoginView(View):
    def get(self, request):
        username = request.COOKIES.get('username', '')

        checked = 'checked' if username else ''

        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整!'})

        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误!'})

        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '用户未激活!'})

        login(request, user)

        next_url = request.GET.get('next', reverse('goods:index'))

        response = redirect(next_url)

        remember = request.POST.get('remember')

        if remember == 'on':
            response.set_cookie('username', username, max_age=7 * 24 * 3600)
        else:
            response.delete_cookie('username')

        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('user:login'))


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


class UserInfoView(LoginRequredMixIn):
    def get(self, request):
        # 获取个人信息
        address = Address.objects.get_default_address(request.user)
        # 获取浏览记录
        conn = get_redis_connection('default')

        history_key = 'history_%d' % request.user.id

        sku_ids = conn.lrange(history_key, 0, 4)

        goods_list = []

        # 历史浏览记录排序
        for sku_id in sku_ids:
            goods = GoodsSKU.objects.get(pk=sku_id)
            goods_list.append(goods)

        context = {
            'page': 'user',
            'address': address,
            'goods_list': goods_list
        }

        return render(request, 'user_center_info.html', context)


class UserOrderView(LoginRequredMixIn):
    def get(self, request):
        # 获取用户的订单信息
        return render(request, 'user_center_order.html', {'page': 'order'})


class AddressView(LoginRequredMixIn):
    def get(self, request):
        # 获取用户的默认收货地址

        address = Address.objects.get_default_address(request.user)

        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'page': 'address', 'errmsg': '数据不完整!'})

        reg = '1([38][0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|9[89])\d{8}'
        if not re.match(reg, phone):
            return render(request, 'user_center_site.html', {'page': 'address', 'errmsg': '手机号码格式错误!'})

        address = Address.objects.get_default_address(request.user)

        is_dafault = False if address else True

        Address.objects.create(
            user=request.user,
            receiver=receiver,
            zip_code=zip_code,
            addr=addr,
            phone=phone,
            is_default=is_dafault,
        )

        return redirect(reverse('user:address'))
