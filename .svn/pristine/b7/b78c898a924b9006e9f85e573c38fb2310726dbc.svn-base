from django.conf import settings
from celery import Celery
from django.core.mail import send_mail

broker = settings.REDIS_URL.format(8)

app = Celery('celery_tasks.task', broker=broker)


@app.task
def send_register_mail(to_email, username, token):
    subject = '生鲜商城欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>{}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://{}/user/active/{}" style="color: green">点击激活</a>'.format(
        username, settings.DOMAIN, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
