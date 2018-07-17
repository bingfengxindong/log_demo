from django.shortcuts import render,redirect
from . import models
from . import forms
from django.conf import settings
import hashlib
import datetime
# Create your views here.
def hash_code(s,salt="mysite"):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def make_confirm_string(new_user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(new_user.name,now)
    models.ConfirmString.objects.create(code=code,user=new_user)
    return code

def set_email(email,code):
    from django.core.mail import EmailMultiAlternatives
    subject = "来自zpf的注册确认邮件"
    text_content = "感谢您注册本网站，如果您看到此消息，说明您的邮箱不具备HTML连接功能，请联系管理员！"
    html_content = """
                <p>感谢注册<a href="http://{}/confirm?code={}" target=blank>www.zpf.com</a>,\
                这是zpf的网站，欢迎注册！</p>
                <p>请点击链接确认！</p>
                <p>此连接有效期为{}天！</p>
                """.format("127.0.0.1:8000",code,settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject,text_content,settings.EMAIL_HOST_USER,[email])
    msg.attach_alternative(html_content,"text/html")
    msg.send()

def index(request):
    pass
    return render(request,"login/index.html")

def login(request):
    if request.session.get("is_login",None):
        return redirect("/index")
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = "该用户还未通过邮件确认！"
                    return render(request,"login/login.html",locals())
                if user.passwd == hash_code(password):
                    request.session["is_login"] = True
                    request.session["user_id"] = user.id
                    request.session["user_name"] = user.name
                    return redirect("/index")
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request,"login/login.html",locals())
    login_form = forms.UserForm()
    return render(request,"login/login.html",locals())

def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User()
                new_user.name = username
                new_user.passwd = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                code = make_confirm_string(new_user)
                set_email(email,code)

                return redirect('/login/')  # 自动跳转到登录页面
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

def user_confirm(request):
    code = request.GET.get("code",None)
    message = ""
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = "无效的确认请求！"
        return render(request,"login/confirm.html",locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = "您的邮件已经过期，请重新注册！"
        return render(request, "login/confirm.html", locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = "感谢确认，请使用账户登录！"
        return render(request,"login/confirm.html",locals())

def logout(request):
    if not request.session.get("is_login",None):
        return redirect("/index")
    request.session.flush()
    return redirect("/index")