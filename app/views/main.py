from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.forms import PostsForm
from flask_login import current_user
from app.extensions import db
from app.models import Posts, User

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostsForm()
    if form.validate_on_submit():
        # 判断是否登录，登录才可以发表博客
        if current_user.is_authenticated:
            # 获取原生user对象，不会写进数据库，但是要用
            u = current_user._get_current_object()
            # 根据表单提交的数据创建表单
            p = Posts(content=form.content.data, user=u)
            # 写入数据库
            db.session.add(p)
            flash('您的博客发表成功啦~~~')
            return redirect(url_for('main.index'))
        else:
            flash('需要登录才能发表博客哦~~~')
            return redirect(url_for('user.login'))

    # 获取博客信息,展示信息
    # posts = Posts.query.filter_by(rid=0).order_by(Posts.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Posts.query.filter_by(rid=0).order_by(Posts.timestamp.desc()).paginate(page=page,per_page=5, error_out=False)
    posts = pagination.items
    return render_template('main/index.html', form=form, posts=posts, pagination=pagination)


# 显示一个人发过的所有博客
@main.route('/usermessage/<username>/')
def usermessage(username):
    page = request.args.get('page', 1, type=int)
    u = User.query.filter_by(username=username).first()
    pagination = Posts.query.filter_by(user=u, rid=0).order_by(Posts.timestamp.desc()).paginate(page=page, per_page=5,
                                                                                       error_out=False)
    posts = pagination.items
    return render_template('main/show_usermessage.html', posts=posts, pagination=pagination, username=username)


# 评论博客
@main.route('/comment/<pid>/', methods=['GET', 'POST'])
def comment(pid):
    # 根据点击的文章的id从数据库获得该篇文章的详细信息
    oldposts = Posts.query.filter_by(id=pid).all()
    #获得想要评论的那个用户的对象
    # u = oldposts[0].user
    commentform = PostsForm()
    if commentform.validate_on_submit():
        # 判断用户是否登录
        if current_user.is_authenticated:
            u = current_user._get_current_object()
            # 模型Posts中rid=0表示博客，rid=1表示评论
            comment = Posts(rid=pid,content=commentform.content.data, user=u)
            # 写进数据库
            db.session.add(comment)
            flash('评论成功！')
            return redirect(url_for('main.comment', pid=pid))
        else:
            flash('亲，需要登录才能评论哦^-^')
            return redirect(url_for('user.login'))
    # 获得评论的消息
    # commentpost = Posts.query.filter_by(rid=pid).all()
    page = request.args.get('page', 1, type=int)
    pagination = Posts.query.filter_by(rid=pid).order_by(Posts.timestamp.desc()).paginate(page=page, per_page=5, error_out=False)
    commentpost = pagination.items
    return render_template('main/comment.html',posts=oldposts, form=commentform,
                           commentpost=commentpost, pid=pid, pagination=pagination)

@main.route('/jiami/')
def jiami():
    return generate_password_hash('123456')

@main.route('/check/<password>')
def check(password):
    # 密码校验函数：加密后的值  密码
    # 正确：True，错误：False
    if check_password_hash('pbkdf2:sha256:50000$43bAaPip$1234ce03524effc32c135e5171ca20fbbcdb30a20049aea8d1546114ec9e932d',
                        password):
        return '密码正确'
    return '密码错误'

@main.route('/generate_token/')
def generate_token():
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
    # 加密指定的数据，以字典的形式传入
    return s.dumps({'id':250})

@main.route('/activate/<token>/')
def activaate(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return 'token有误'
    return str(data.get('id'))