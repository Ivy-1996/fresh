from django.shortcuts import render, redirect, reverse
from django.views import View
from apps.goods.models import *
from apps.order.models import OrderGoods
from django_redis import get_redis_connection


# Create your views here.

class IndexView(View):
    def get(self, request):
        # 获取商品种类
        types = GoodsType.objects.all()
        # 获取首页轮播商品信息
        GoodsBanner = IndexGoodsBanner.objects.all().order_by('index')
        # 获取首页活动信息
        PromotionBanner = IndexPromotionBanner.objects.all().order_by('index')
        # 获取首页分类商品展示信息
        for type in types:
            type.img_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
            type.tltle_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 获取购物车商品数量
        cart_count = 0
        if request.user.is_authenticated:
            coon = get_redis_connection('default')
            cart_key = 'cart_%d' % request.user.id
            cart_count = coon.hlen(cart_key)

        # 模板上下文
        context = {
            'types': types,
            'GoodsBanner': GoodsBanner,
            'PromotionBanner': PromotionBanner,
            'cart_count': cart_count,
        }

        return render(request, 'index.html', context)


class DetailView(View):
    def get(self, request, pk):
        # 查询商品id是否存在
        try:
            sku = GoodsSKU.objects.get(pk=pk)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = Goods.objects.all()
        # 获取商品的评论
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')
        # 获取购物车商品数量
        cart_count = 0
        if request.user.is_authenticated:
            coon = get_redis_connection('default')
            cart_key = 'cart_%d' % request.user.id
            cart_count = coon.hlen(cart_key)

        context = {
            'sku': sku,
            'types': types,
            'sku_order': sku_orders,
            'new_skus': new_skus,
            'cart_count': cart_count,
        }

        return render(request, 'detail.html', context)
