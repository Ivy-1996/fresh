from django.shortcuts import redirect, reverse, render
from goods.models import GoodsSKU
from user.models import Address
from django_redis import get_redis_connection
from utils.mixin import LoginRequredMixIn
from django.http import JsonResponse
from order.models import OrderInfo, OrderGoods
from datetime import datetime


# Create your views here.

class OrderPlaceView(LoginRequredMixIn):
    def post(self, request):

        user = request.user

        sku_ids = request.POST.getlist('sku_ids')

        if not sku_ids:
            return redirect(reverse('cart:show'))

        coon = get_redis_connection('default')

        cart_key = 'cart_%d' % user.id

        skus = []
        total_count = 0
        total_price = 0

        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(pk=sku_id)
            # 获取商品的数量
            conut = coon.hget(cart_key, sku_id)
            amount = sku.price * int(conut)
            sku.count = int(conut.decode())
            sku.amount = amount
            skus.append(sku)
            total_count += int(conut)
            total_price += amount

        # 运费
        transit_price = 10  # 假数据， 写死
        # 实付费
        total_pay = total_price + transit_price

        addrs = Address.objects.filter(user=user)

        sku_ids = ",".join(sku_ids)

        # 组织上下文
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': transit_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }

        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequredMixIn):
    def post(self, request):
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '用户未登录!'})

        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')

        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整!'})

        # todo 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式!'})

        try:
            addr = Address.objects.get(pk=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        # TODO: 创建订单
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        # 运费
        transit_price = 10  # 假数据， 写死
        total_count = 0
        total_price = 0
        # TODO  想订单信息表中添加一条记录
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            addr=addr,
            pay_method=pay_method,
            total_count=total_count,
            total_price=total_price,
            transit_price=transit_price
        )

        coon = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # todo 用户的订单中有几个商品就要添加几条记录
        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                return JsonResponse({'res': 4, 'errmsg': '商品不存在!'})

            # 获取商品的数目
            count = coon.hget(cart_key, sku_id)

            # todo to订单信息表中添加一条记录
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=int(count),
                price=sku.price,
            )

            # todo 更新商品的库存销量和库存
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()

            # todo 累加计算商品的订单的总数量和总价格
            amount = sku.price * int(count)
            total_count += int(count)
            total_price += amount

        # todo 更新订单信息表中的商品的总数量和价格
        order.total_count = total_count
        order.total_price = total_price
        order.save()

        # todo 清楚用户的购物车记录
        coon.hdel(cart_key, *sku_ids)

        return JsonResponse({'res': 5, 'message': '创建成功!'})
