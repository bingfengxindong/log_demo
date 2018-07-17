import os
from django.core.mail import send_mail,EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE'] = 'log_demo.settings'

if __name__ == '__main__':

    # send_mail(
    #     '来自zpf的测试邮件',
    #     'hello zpf！',
    #     '15736950639@163.com',
    #     ['1071251364@qq.com'],
    # )
    subject,from_email,to = "来自zpf的测试邮件","15736950639@163.com","1071251364@qq.com"
    text_content = "hello zpf!"
    html_content = "<p>欢迎访问<a href='https://www.baidu.com' target=blank>hello</a></p>"
    msg = EmailMultiAlternatives(subject,text_content,from_email,[to])
    msg.attach_alternative(html_content,"text/html")
    msg.send()