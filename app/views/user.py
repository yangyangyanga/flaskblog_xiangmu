import os
from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request, g, session
from app.forms import RegisterForm, LoginForm, PasswordForm, EmailForm, UploadPhoto, IdentifyForm, FindPasswordForm
from app.email import send_mail
from app.models import User
from app.extensions import db, photo
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

user = Blueprint('user', __name__)

@user.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 创建对象
        u = User(username=form.username.data, password=form.password.data,
                 email=form.email.data)
        # 执行，写入数据库
        db.session.add(u)
        # 因为下面产生token时需要用到用户id，此时还没有用户id
        db.session.commit()
        # 生成token
        token = u.generate_activate_token()
        # 发送激活邮件
        send_mail(form.email.data, '账户激活', 'email/account_activate',
                  token=token, username=form.username.data)
        flash('激活邮件已发送，请点击链接完成用户激活')
        return redirect(url_for('main.index'))
    return render_template('user/register.html', form=form)

@user.route('/activate/<token>')
def activate(token):
    if User.check_activate_token(token):
        flash('账户激活成功')
        return redirect(url_for('user.login'))
    else:
        flash('账户激活失败')
        return redirect(url_for('main.index'))

@user.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u is None:
            flash('无效的用户名')
        elif u.verify_password(form.password.data):
            # 验证通过，用户登录，顺便可以完成记住的功能
            login_user(u, remember=form.remember_me.data)
            # 如果有下一跳转地址就跳转到指定地址，没有跳转到首页
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('无效的密码')
    return render_template('user/login.html', form=form)

@user.route('/logout/')
@login_required     # 保护路由
def logout():
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))

@user.route('/profile/')
@login_required
def profile():
    return render_template('user/profile.html')

@user.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_pwd.data):
            current_user.password = form.new_pwd.data
            db.session.add(current_user)
            flash('密码修改成功，下次请使用新密码')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码')
            return redirect(url_for('user.change_password'))
    return render_template('user/change_password.html', form=form)

@user.route('/change_email/', methods=['GET', 'POST'])
@login_required
def change_email():
    form = EmailForm()
    if form.validate_on_submit():
        if form.old_email.data == current_user.email:
            # 生成token
            token = current_user.generate_activate_token()
            # 发送邮件
            send_mail(form.old_email.data, '新邮箱激活', 'email/change_email',
                      token=token, username=current_user.username, new_email=form.new_email.data)
            current_user.email = form.new_email.data
            flash('邮箱修改完成，请点击链接激活~~~')
            return redirect(url_for('main.index'))
        else:
            flash('无效的邮箱')
            return redirect(url_for('user.change_email'))
    return render_template('user/change_email.html', form=form)

# 生成随机的字符串
def rand_str(length=32):
    import random
    base_str = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))
@user.route('/upload_photo/', methods=['GET', 'POST'])
@login_required
def upload_photo():
    form = UploadPhoto()
    img_url = None
    if form.validate_on_submit():
        # 获得上传图片的后缀
        suffix = os.path.splitext(form.photo.data.filename)[1]
        name = rand_str() + suffix
        # 保存上传图片
        photo.save(form.photo.data, name=name)
        # 获得图片保存的路径位置
        photoname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], name)
        # 对该图片进行缩略
        img = Image.open(photoname)
        img.thumbnail((128, 128))
        img.save(photoname)
        # 将上一次的头像删除
        if current_user.photo_url != 'default.jpg':
            os.remove(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], current_user.photo_url))
        # 保存图片的名字到user表中
        current_user.photo_url = name
        db.session.add(current_user)
        flash('你的头像已更换~~~')
        # return redirect(url_for('user.profile'))
    return render_template('user/upload_photo.html', form=form)

@user.route('/identify/', methods=['GET', 'POST'])
def identify():
    form = IdentifyForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.old_username.data).first()
        if u:
            token = u.generate_activate_token()
            send_mail(form.email.data, '找回密码', 'email/find_password',
                      token=token, username=form.old_username.data)
            flash('找回密码验证邮件已经发送，请去修改密码~~~')
            return redirect(url_for('user.login'))
    return render_template('user/identify.html', form=form)
@user.route('/find_password/<token>/', methods=['GET', 'POST'])
def find_password(token):
    form = FindPasswordForm()
    if User.check_activate_token(token):
        flash('该用户验证成功，请修改密码~~~')
        if form.validate_on_submit():
            data = Serializer(current_app.config['SECRET_KEY']).loads(token)
            u = User.query.get(data.get('id'))
            u.password = form.newpwd.data
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('user.login'))
        return render_template('user/find_password.html', form=form)
    else:
        flash('用户验证不对')
        redirect(url_for('user.identify'))