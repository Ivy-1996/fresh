from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from utils.mixin import LoginRequredMixIn


# Create your views here.

class CartAddView(View):
    def post(self, request):

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录!'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整!'})

        try:
            count = int(count)
        except Exception:
            return JsonResponse({'res': 2, 'errmsg': '商品数目错误'})

        try:
            sku = GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        coon = get_redis_connection('default')

        cart_key = 'cart_%d' % user.id

        cart_count = coon.hget(cart_key, sku_id)

        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '存库不足!'})

        if cart_count:
            count += int(cart_count)

        # 设置hash中sku对应得值
        coon.hset(cart_key, sku_id, count)

        total_count = coon.hlen(cart_key)

        return JsonResponse({'res': 5, 'message': '添加成功!', 'total_count': total_count})


class CartInfoView(LoginRequredMixIn):
    def get(self, request):
        user = request.user
        # 获取购物车商品信息
        coon = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        cart_dict = coon.hgetall(cart_key)

        skus = []
        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(pk=sku_id)
            amount = sku.price * int(count)
            sku.amount = amount
            sku.count = int(count)
            skus.append(sku)
            total_count += int(count)
            total_price += amount

        context = {
            'total_count': total_count,
            'total_price': total_price,
            'skus': skus
        }

        return render(request, 'cart.html', context)


# 购物车记录更新
class CartUpdateView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整!'})

        try:
            count = int(count)
        except Exception:
            return JsonResponse({'res': 2, 'errmsg': '商品数目错误'})

        try:
            sku = GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        coon = get_redis_connection('default')

        cart_key = 'cart_%d' % user.id

        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '存库不足!'})

        # 设置hash中sku对应得值
        coon.hset(cart_key, sku_id, count)

        values = coon.hvals(cart_key)

        total_count = sum(values)

        return JsonResponse({'res': 5, 'message': '更新成功!', 'total_count': total_count})


class CartDeleteView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        sku_id = request.POST.get('sku_id')

        if not sku_id:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品id'})

        try:
            GoodsSKU.objects.get(pk=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 2, 'errmsg': '商品不存在!'})

        coon = get_redis_connection('default')

        cart_key = 'cart_%d' % user.id

        coon.hdel(cart_key, sku_id)

        values = coon.hvals(cart_key)

        values = [int(value.decode()) for value in values]


        total_count = sum(values)

        return JsonResponse({'res': 3, 'message': '删除成功!', 'total_count': total_count})
