from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU


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
