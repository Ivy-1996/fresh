import xadmin
from .models import *


class GoodsTypeAdmin(object):
    list_display = ['id', 'name', 'logo', 'image']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'create_time', 'update_time']
    list_filter = ['create_time', 'update_time', 'delflag']


class GoodsSKUAdmin(object):
    list_display = ['id', 'name', 'detail']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'create_time', 'update_time']
    list_filter = ['create_time', 'update_time', 'delflag']

class GoodsAdmin(object):
    list_display = ['id', 'type', 'goods', 'name', 'price', 'unite']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'create_time', 'update_time']
    list_filter = ['create_time', 'update_time', 'delflag']

class GoodsImageAdmin(object):
    list_display = ['id', 'sku', 'image']
    list_display_links = ['id', 'sku']
    search_fields = ['name', 'create_time', 'update_time']
    list_filter = ['create_time', 'update_time', 'delflag']


xadmin.site.register(GoodsType, GoodsTypeAdmin)
xadmin.site.register(GoodsSKU, GoodsSKUAdmin)
xadmin.site.register(Goods, GoodsSKUAdmin)
xadmin.site.register(GoodsImage, GoodsImageAdmin)
xadmin.site.register(IndexGoodsBanner)
xadmin.site.register(IndexTypeGoodsBanner)
xadmin.site.register(IndexPromotionBanner)
