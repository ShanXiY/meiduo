# 5. 发送激活邮件
from django.conf import settings
from django.core.mail import send_mail

from users.utils import generic_active_url
from celery_tasks.main import app

@app.task(name='send_active_email')
def send_active_email(email,user_id):
    subject = '美多商城激活邮件' #主题

    message = '内容' #内容

    from_email = settings.EMAIL_FROM #发件人


    recipient_list = [email]  #接收人列表

    #可以设置一些html的样式等信息
    verify_url = generic_active_url(user_id,email)

    html_message = '<p>尊敬的用户您好！</p>' \
               '<p>感谢您使用美多商城。</p>' \
               '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
               '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message
)