from xadmin import views
import xadmin


# 配置xadmin主题
class BaseSettingAdmin(object):
    enable_themes = True
    use_bootswatch = True


class CommSettingAdmin(object):
    site_title = 'Django-天天生鲜后台管理系统'
    site_footer = 'ivy'
    menu_style = 'accordion'  # 折叠样式


# 注册主题类
xadmin.site.register(views.BaseAdminView, BaseSettingAdmin)
# 注册全局样式类
xadmin.site.register(views.CommAdminView, CommSettingAdmin)
