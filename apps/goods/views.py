from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
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
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[0:2]

        # 获取同一商品spu的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(pk=pk)

        # 获取购物车商品数量
        cart_count = 0
        if request.user.is_authenticated:
            coon = get_redis_connection('default')
            cart_key = 'cart_%d' % request.user.id
            cart_count = coon.hlen(cart_key)

            # 添加用户的历史浏览记录
            coon = get_redis_connection('default')
            history_key = 'history_%d' % request.user.id
            # 移除之前的该商品id
            coon.lrem(history_key, 0, pk)
            # 把goods_id左侧插入redis列表
            coon.lpush(history_key, pk)
            # 取用户保存的最新5条信息
            coon.ltrim(history_key, 0, 4)

        context = {
            'sku': sku,
            'types': types,
            'sku_order': sku_orders,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'same_spu_skus': same_spu_skus
        }

        return render(request, 'detail.html', context)


class ListView(View):
    def get(self, request, type_id, page):
        # 获取种类信息
        try:
            type = GoodsType.objects.get(pk=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        types = GoodsType.objects.all()

        sort = request.GET.get('sort', 'default')
        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('sales')
        else:
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        paginator = Paginator(skus, 1)

        # 对页码进行容错处理
        try:
            page = int(page)
        except Exception:
            page = 1

        if page > paginator.num_pages:
            page = paginator.num_pages

        skus_page = paginator.page(page)

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[0:2]

        # 获取购物车商品数量
        cart_count = 0
        if request.user.is_authenticated:
            coon = get_redis_connection('default')
            cart_key = 'cart_%d' % request.user.id
            cart_count = coon.hlen(cart_key)

        context = {
            'type': type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort
        }

        return render(request, 'list.html', context)
