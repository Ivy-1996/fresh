from django.shortcuts import render
from django.views import View
from apps.goods.models import *


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
        cart_count = 2
        # 模板上下文
        context = {
            'types': types,
            'GoodsBanner': GoodsBanner,
            'PromotionBanner': PromotionBanner,
            'cart_count': cart_count,
        }
        return render(request, 'index.html', context)
