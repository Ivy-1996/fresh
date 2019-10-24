# python-django B2C-分布式生鲜商城

### 项目实例地址：
[https://fresh.summerleaves.cn/](https://fresh.summerleaves.cn/)
####  后台体验
   * [https://fresh.summerleaves.cn/xadmin/](https://fresh.summerleaves.cn/xadmin/)
   * 账号：`fresh`
   * 密码: `django123`
###  技术栈
* 语言：Python3.6.8  (Django==2.1.5)
* 数据库: MySql、 redis
* 任务队列(异步处理): celery
* 分布式文件存储: FastDFS
* 搜索引擎(商品检索)： django-haystack 、whoosh
* web服务器配置: Nginx+ uwsgi
* 后台管理: django-xadmin


###  安装和配置
* 安装python3.6
* 安装依赖包  
    * 安装PIP安装FASTDFS可能会有异常
    * 进入项目根目录提供的requirement文件夹,进入fdfs_client-py-master
        * `python setup.py install`等待安装完毕即可
    * 安装xadmin
        * 找到xadmin的压缩包`pip install xadmin-django2.zip`'
    * 进入项目根目录`pip install -r requeirtments.txt`
* 配置数据库
    * setting文件配置好mysql数据库
    * 填入`REDIS_CONFIG`的配置信息
    * 生成迁移文件
        * `python manager.py makemigrations`
    * 应用迁移
        * `python manager.py migrate`
* 配置eamil
    * `EMAIL_HOST_USER`
    * `EMAIL_HOST_PASSWORD`
    * `EMAIL_HOST_PASSWORD`
    * 参考链接：
        * https://www.cnblogs.com/ivy-blogs/p/10961494.html
        * https://www.cnblogs.com/ivy-blogs/p/11180271.html
* 修改DOMAIL
    * `DOMAIN` 修改为你的启动项目的ip地址或域名
* 修改IMG_URL
    * `IMG_URL` 修改为你的fast-dfs配置的nginx映射的ip和域名
* 修改fast-dfs的配置
* 修改`ALIPAY_APP_ID`为你的id
    * 参考链接
        * https://docs.open.alipay.com/200/105311/
* 安装fast-dfs和配置
    * 参考链接：
        * https://www.cnblogs.com/ivy-blogs/p/11237118.html
* uwsgi + nginx 项目部署
    * 参考链接
        * https://www.cnblogs.com/ivy-blogs/p/11162464.
        
flask重构版：`https://github.com/Ivy-1996/flask-fresh`
